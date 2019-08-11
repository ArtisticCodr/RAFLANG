""" SCI - Simple C Interpreter """

from ..lexical_analysis.token_type import *
from .tree import *
from ..utils.utils import restorable


class SyntaxError(Exception):
    pass


class Parser(object):

    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token  # set current token to the first token taken from the input

    def error(self, message):
        raise SyntaxError(message)

    def eat(self, token_type):
        """ Compare the current token type with the passed token
        type and if they match then "eat" the current token
        and assign the next token to the self.current_token,
        otherwise raise an exception. """

        print(self.current_token.type)
        print(self.current_token.value)
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token
        else:
            self.error(
                'Expected token <{}> but found <{}> at line {}.'.format(
                    token_type, self.current_token.type, self.lexer.line
                )
            )

    def program(self):
        """
        program                     : declarations
        """
        root = Program(
            declarations=self.declarations(),
            line=self.lexer.line

        )
        return root

    def declarations(self):
        """
        declarations                : (include_library | function_declaration | declaration_list)*
        """
        declarations = []

        while self.current_token.type in [CHAR, FLOAT, DOUBLE, INT, LEARN, STR_TYPE]:
            if self.current_token.type == LEARN:
                lib = self.include_library()
                if lib != -1:
                    declarations.append(lib)
                else:
                    continue
            else:
                response = self.check_function()
                if response == 1:
                    declarations.append(self.function_declaration())
                elif response == 2:
                    declarations.append(self.opening_declaration())
                else:
                    declarations.extend(self.declaration_list())
        return declarations

    def include_library(self):
        """
        include_library             : HASH ID<'include'> LESS_THAN ID DOT ID<'h'> GREATER_THAN
        """
        self.eat(LEARN)
        self.eat(BRLEFT)
        
        directory = ""
        while self.current_token.type != DOT:
            directory += self.current_token.value
            self.eat(self.current_token.type)
        
        self.eat(DOT)
        extension = self.current_token
        if extension.value != 'rl':
            self.error(
                'You can include only *.rl files [line {}]'.format(self.lexer.line)
            )
        self.eat(ID)
        
        
        if directory == 'stdio' or directory == 'math':
            self.eat(BRRIGHT)
            return IncludeLibrary(
                library_name=directory,
                line=self.lexer.line
                )
        else:
            self.lexer.includeLib(directory)
            self.eat(BRRIGHT)
            return -1

    @restorable
    def check_function(self):
        self.eat(self.current_token.type)
        token = self.current_token
        self.eat(token.type)
        
        if token.value == 'opening':
            return 2
        
        if token.value == 'func':
            return 1
        else:
            return 0

    
    def opening_declaration(self):
        """
        function_declaration        : type_spec opening compound_statement
        """
        type_node = self.type_spec()
        func_name = self.current_token.value
        self.eat(ID)

        params = []

        return FunctionDecl(
            type_node=type_node,
            func_name=func_name,
            params=params,
            body=self.function_body(),
            line=self.lexer.line
        )

    def function_declaration(self):
        """
        function_declaration        : type_spec FUNC COLON ID COMMA parameters COLON CUNF compound_statement
        """
        type_node = self.type_spec()
        self.eat(FUNC)
        self.eat(COLON)
        func_name = self.current_token.value
        self.eat(ID)
        self.eat(COMMA)
        params = self.parameters()
        self.eat(COLON)
        self.eat(CUNF)
        return FunctionDecl(
            type_node=type_node,
            func_name=func_name,
            params=params,
            body=self.function_body(),
            line=self.lexer.line
        )

    def function_body(self):
        """
        function_body               : LBRACKET (declaration_list | statement)* RBRACKET
        """
        result = []
        self.eat(LBRACKET)
        while self.current_token.type != RBRACKET:
            if self.current_token.type in (CHAR, INT, FLOAT, DOUBLE, STR_TYPE):
                result.extend(self.declaration_list())
            elif self.current_token.type == INJECT:
                self.inject()
                continue
            else:
                result.append(self.statement())
        self.eat(RBRACKET)
        return FunctionBody(
            children=result,
            line=self.lexer.line
        )

    def inject(self):
        self.eat(INJECT)
        self.eat(BRLEFT)
        
        directory = ""
        while self.current_token.type != DOT:
            directory += self.current_token.value
            self.eat(self.current_token.type)
        
        self.eat(DOT)
        extension = self.current_token
        if extension.value != 'rl':
            self.error(
                'You can include only *.rl files [line {}]'.format(self.lexer.line)
            )
        self.eat(ID)
        
        self.lexer.includeLib(directory)
        self.eat(BRRIGHT)

    def parameters(self):
        """
        parameters                  : type_spec variable (COMMA type_spec variable)*
        """
        nodes = []
        if self.current_token.type != RPAREN:
            nodes = [Param(
                type_node=self.type_spec(),
                var_node=self.variable(),
                line=self.lexer.line
            )]
            while self.current_token.type == COMMA:
                self.eat(COMMA)
                nodes.append(Param(
                    type_node=self.type_spec(),
                    var_node=self.variable(),
                    line=self.lexer.line
                ))
        return nodes

    def declaration_list(self):
        """
        declaration_list            : declaration+
        """
        result = self.declaration()
        while self.current_token.type == (CHAR, INT, FLOAT, DOUBLE, STR_TYPE):
            result.extend(self.declaration())
        return result

    def declaration(self):
        """
        declaration                 : type_spec init_declarator_list SEMICOLON
        """
        result = list()
        type_node = self.type_spec()
        for node in self.init_declarator_list():
            if isinstance(node, Var):
                result.append(VarDecl(
                    type_node=type_node,
                    var_node=node,
                    line=self.lexer.line
                ))
            else:
                result.append(node)
        self.eat(SEMICOLON)
        return result

    def init_declarator_list(self):
        """
        init_declarator_list        : init_declarator (COMMA init_declarator)*
        """
        result = list()
        result.extend(self.init_declarator())
        while self.current_token.type == COMMA:
            self.eat(COMMA)
            result.extend(self.init_declarator())
        return result

    def init_declarator(self):
        """
        init_declarator             : variable (ASSIGN assignment_expression)?
        """
        var = self.variable()
        result = list()
        result.append(var)
        if self.current_token.type == ASSIGN:
            token = self.current_token
            self.eat(ASSIGN)
            result.append(Assign(
                left=var,
                op=token,
                right=self.assignment_expression(),
                line=self.lexer.line
            ))
        return result

    def statement(self):
        """
        statement                   : iteration_statement
                                    | selection_statement
                                    | jump_statement
                                    | compound_statement
                                    | expression_statement
        """
        if self.check_iteration_statement():
            return self.iteration_statement()
        elif self.check_selection_statement():
            return self.selection_statement()
        elif self.check_jump_statement():
            return self.jump_statement()
        elif self.check_compound_statement():
            return self.compound_statement()
        return self.expression_statement()

    @restorable
    def check_compound_statement(self):
        return self.current_token.type == LBRACKET

    def compound_statement(self):
        """
        compound_statement          : LBRACKET (declaration_list | statement)* RBRACKET
        """
        result = []
        self.eat(LBRACKET)
        while self.current_token.type != RBRACKET:
            if self.current_token.type in (CHAR, INT, FLOAT, DOUBLE):
                result.extend(self.declaration_list())
            else:
                result.append(self.statement())
        self.eat(RBRACKET)
        return CompoundStmt(
            children=result,
            line=self.lexer.line
        )

    @restorable
    def check_jump_statement(self):
        return self.current_token.type in (RETURN, BREAK, CONTINUE)

    def jump_statement(self):
        """
        jump_statement              : RETURN expression? SEMICOLON
                                    | BREAK SEMICOLON
                                    | CONTINUE SEMICOLON
        """
        if self.current_token.type == RETURN:
            self.eat(RETURN)
            expression = self.empty()
            if self.current_token.type != SEMICOLON:
                expression = self.expression()
            self.eat(SEMICOLON)
            return ReturnStmt(
                expression=expression,
                line=self.lexer.line
            )
        elif self.current_token.type == BREAK:
            self.eat(BREAK)
            self.eat(SEMICOLON)
            return BreakStmt(
                line=self.lexer.line
            )

        elif self.current_token.type == CONTINUE:
            self.eat(CONTINUE)
            self.eat(SEMICOLON)
            return ContinueStmt(
                line=self.lexer.line
            )

    @restorable
    def check_selection_statement(self):
        return self.current_token.type == IF

    def selection_statement(self):
        """
        selection_statement         : IF LPAREN expression RPAREN statement (ELSE statement)?
        """
        if self.current_token.type == IF:
            self.eat(IF)
            condition = self.expression()
            self.eat(IFRPAREN)
            tstatement = self.statement()
            fstatement = self.empty()
            if self.current_token.type == ELSE:
                self.eat(ELSE)
                fstatement = self.statement()
            return IfStmt(
                condition=condition,
                tbody=tstatement,
                fbody=fstatement,
                line=self.lexer.line
            )

    @restorable
    def check_iteration_statement(self):
        return self.current_token.type in (WHILE, DO, FROM)

    def iteration_statement(self):
        """
        iteration_statement         : WHILE LPAREN expression RPAREN statement
                                    | DO statement WHILE LPAREN expression RPAREN SEMICOLON
                                    | FOR LPAREN expression_statement expression_statement (expression)? RPAREN statement
        """
        if self.current_token.type == WHILE:
            self.eat(WHILE)
            expression = self.expression()
            self.eat(ELIHW)
            statement = self.statement()
            return WhileStmt(
                condition=expression,
                body=statement,
                line=self.lexer.line
            )
        elif self.current_token.type == DO:
            self.eat(DO)
            statement = self.statement()
            self.eat(WHILE)
            expression = self.expression()
            self.eat(ELIHW)
            return DoWhileStmt(
                condition=expression,
                body=statement,
                line=self.lexer.line
            )
        else:
            self.eat(FROM)
            setup = self.from_expression_statement()
            condition = self.repeatto_expression_statement()

            statement = self.statement()
            return ForStmt(
                setup=setup,
                condition=condition,
                body=statement,
                line=self.lexer.line
            )
            
    def repeatto_expression_statement(self):
        """
        expression_statement        : expression* SEMICOLON
        """
        node = None
        if self.current_token.type != COLON:
            node = self.expression()
        self.eat(COLON)
        return node and node or NoOp(line=self.lexer.line)
    
    def from_expression_statement(self):
        """
        expression_statement        : expression* SEMICOLON
        """
        node = None
        if self.current_token.type != REPEATTO:
            node = self.expression()
        self.eat(REPEATTO)
        return node and node or NoOp(line=self.lexer.line)

    def expression_statement(self):
        """
        expression_statement        : expression* SEMICOLON
        """
        node = None
        if self.current_token.type != SEMICOLON:
            node = self.expression()
        self.eat(SEMICOLON)
        return node and node or NoOp(line=self.lexer.line)

    def constant_expression(self):
        """
        constant_expression         : conditional_expression
        """
        return self.conditional_expression()

    def expression(self):
        """
        expression                  : assignment_expression (COMMA assignment_expression)*
        """
        result = list()
        result.append(self.assignment_expression())
        while self.current_token.type == COMMA:
            self.eat(COMMA)
            result.append(self.assignment_expression())
        return Expression(
            children=result,
            line=self.lexer.line
        )

    @restorable
    def check_assignment_expression(self):
        if self.current_token.type == ID:
            self.eat(ID)
            return self.current_token.type.endswith('ASSIGN')
        return False

    def assignment_expression(self):
        """
        assignment_expression       : assignment_expression (COMMA assignment_expression)*
                                    | conditional_expression
        """
        if self.check_assignment_expression():
            node = self.variable()
            while self.current_token.type.endswith('ASSIGN'):
                token = self.current_token
                self.eat(token.type)
                return Assign(
                    left=node,
                    op=token,
                    right=self.assignment_expression(),
                    line=self.lexer.line
                )
        return self.conditional_expression()

    def conditional_expression(self):
        """
        conditional_expression      : logical_and_expression (QUESTION_MARK expression COLON conditional_expression)?
        """
        node = self.logical_and_expression()
        if self.current_token.type == QUESTION_MARK:
            self.eat(QUESTION_MARK)
            texpression = self.expression()
            self.eat(COLON)
            fexpression = self.conditional_expression()
            return TerOp(
                condition=node,
                texpression=texpression,
                fexpression=fexpression,
                line=self.lexer.line
            )
        return node

    def logical_and_expression(self):
        """
        logical_and_expression      : logical_or_expression (LOG_AND_OP logical_or_expression)*
        """
        node = None
        while self.current_token.type == LOG_AND_OP:
            token = self.current_token
            self.eat(token.type)
            node = self.logical_or_expression()
            self.eat(token.type)
            rnode = self.logical_or_expression()
            self.eat(token.type)
            
            node = BinOp(
                left=node,
                op=token,
                right=rnode,
                line=self.lexer.line
            )
        if node == None:
            node = self.logical_or_expression()
        
        return node

    def logical_or_expression(self):
        """
        logical_or_expression       : inclusive_or_expression (LOG_OR_OP inclusive_or_expression)*
        """
        node = None
        while self.current_token.type == LOG_OR_OP:
            token = self.current_token
            self.eat(token.type)
            node = self.inclusive_or_expression()
            self.eat(token.type)
            rnode = self.inclusive_or_expression()
            self.eat(token.type)
            
            node = BinOp(
                left=node,
                op=token,
                right=rnode,
                line=self.lexer.line
            )
        if node == None:
            node = self.inclusive_or_expression()
        
        return node

    def inclusive_or_expression(self):
        """
        inclusive_or_expression     : exclusive_or_expression (OR_OP exclusive_or_expression)*
        """
        node = self.exclusive_or_expression()
        while self.current_token.type == OR_OP:
            token = self.current_token
            self.eat(token.type)
            node = BinOp(
                left=node,
                op=token,
                right=self.exclusive_or_expression(),
                line=self.lexer.line
            )
        return node

    def exclusive_or_expression(self):
        """
        exclusive_or_expression     : and_expression (XOR_OP and_expression)*
        """
        node = self.and_expression()
        while self.current_token.type == XOR_OP:
            token = self.current_token
            self.eat(token.type)
            node = BinOp(
                left=node,
                op=token,
                right=self.and_expression(),
                line=self.lexer.line
            )
        return node

    def and_expression(self):
        """
        and_expression              : equality_expression (AND_OP equality_expression)*
        """
        node = self.equality_expression()
        while self.current_token.type == AND_OP:
            token = self.current_token
            self.eat(token.type)
            node = BinOp(
                left=node,
                op=token,
                right=self.equality_expression(),
                line=self.lexer.line
            )
        return node

    def equality_expression(self):
        """
        equality_expression         : relational_expression ((EQ_OP | NE_OP) relational_expression)*
        """
        node = self.relational_expression()
        while self.current_token.type in (EQ_OP, NE_OP):
            token = self.current_token
            self.eat(token.type)
            return BinOp(
                left=node,
                op=token,
                right=self.relational_expression(),
                line=self.lexer.line
            )
        return node

    def relational_expression(self):
        """
        relational_expression       : shift_expression ((LE_OP | LT_OP | GE_OP | GT_OP) shift_expression)*
        """
        node = self.shift_expression()
        while self.current_token.type in (LE_OP, LT_OP, GE_OP, GT_OP):
            token = self.current_token
            self.eat(token.type)
            return BinOp(
                left=node,
                op=token,
                right=self.shift_expression(),
                line=self.lexer.line
            )
        return node

    def shift_expression(self):
        """
        shift_expression            : additive_expression ((LEFT_OP | RIGHT_OP) additive_expression)*
        """
        node = None
        while self.current_token.type in (LEFT_OP, RIGHT_OP):
            token = self.current_token
            self.eat(token.type)
            node = self.multiplicative_expression()
            self.eat(token.type)            
            rnode = self.multiplicative_expression()

            node = BinOp(
                left=node,
                op=token,
                right=rnode,
                line=self.lexer.line
            )
        else:
            if node == None:
                node = self.multiplicative_expression()
        return node

    def additive_expression(self):
        """
        additive_expression         : multiplicative_expression  multiplicative_expression (ADD_OP | SUB_OP)*
        """
        node = self.cast_expression()
        
        while(self.current_token.type in (CHAR_CONST, INTEGER_CONST, REAL_CONST, LPAREN, STRING, ID)):
            rnode = self.cast_expression()
            if self.current_token.type in (ADD_OP, SUB_OP):
                token = self.current_token
                self.eat(token.type)
                node = BinOp(
                    left=node,
                    op=token,
                    right=rnode,
                    line=self.lexer.line
                    )
            else:
                self.error('Expected token <ADDITIVE> but found <{}> at line {}.'.format(
                    self.current_token.type, self.lexer.line))
        
        return node

    def multiplicative_expression(self):
        """
        multiplicative_expression   : cast_expression ((MUL_OP | DIV_OP | MOD_OP) cast_expression)*
        """
        node = self.additive_expression()
        curentToken = self.current_token
        
        while self.current_token.type in (MUL_OP, DIV_OP, MOD_OP):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(
                left=node,
                op=token,
                right=self.additive_expression(),
                line=self.lexer.line
            )
        return node

    @restorable
    def check_cast_expression(self):
        if self.current_token.type == LPAREN:
            self.eat(LPAREN)
            if self.current_token.type in [CHAR, DOUBLE, INT, FLOAT]:
                self.eat(self.current_token.type)
                return self.current_token.type == RPAREN
        return False

    def cast_expression(self):
        """
        multiplicative_expression   : LPAREN type_spec RPAREN cast_expression
                                    | unary_expression
        """
        if self.check_cast_expression():
            self.eat(LPAREN)
            type_node = self.type_spec()
            self.eat(RPAREN)
            return UnOp(
                op=type_node.token,
                expr=self.cast_expression(),
                line=self.lexer.line
            )
        else:
            return self.unary_expression()

    def unary_expression(self):
        """
        unary_expression            : INC_OP unary_expression
                                    | DEC_OP unary_expression
                                    | AND_OP cast_expression
                                    | ADD_OP cast_expression
                                    | SUB_OP cast_expression
                                    | LOG_NEG cast_expression
                                    | postfix_expression
        """
        if self.current_token.type in (INC_OP, DEC_OP):
            token = self.current_token
            self.eat(token.type)
            return UnOp(
                op=token,
                expr=self.unary_expression(),
                line=self.lexer.line
            )
        elif self.current_token.type in (AND_OP, ADD_OP, SUB_OP, LOG_NEG):
            token = self.current_token
            self.eat(token.type)
            return UnOp(
                op=token,
                expr=self.cast_expression(),
                line=self.lexer.line
            )
        else:
            return self.postfix_expression()

    def postfix_expression(self):
        """
        unary_expression            : primary_expression INC_OP
                                    | primary_expression DEC_OP
                                    | primary_expression LPAREN argument_expression_list? RPAREN
        """
        node = self.primary_expression()
        if self.current_token.type in (INC_OP, DEC_OP):
            token = self.current_token
            self.eat(token.type)
            node = UnOp(
                op=token,
                expr=node,
                line=self.lexer.line,
                prefix=False
            )
        elif self.current_token.type == LPAREN:
            self.eat(LPAREN)
            args = list()
            if not self.current_token.type == RPAREN:
                args = self.argument_expression_list()
            self.eat(RPAREN)
            if not isinstance(node, Var):
                self.error("Function identifier must be string")
            node = FunctionCall(
                name=node.value,
                args=args,
                line=self.lexer.line
            )
        return node

    def argument_expression_list(self):
        """
        argument_expression_list    : assignment_expression (COMMA assignment_expression)*
        """
        args = [self.assignment_expression()]
        while self.current_token.type == COMMA:
            self.eat(COMMA)
            args.append(self.assignment_expression())
        return args

    def primary_expression(self):
        """
        primary_expression          : LPAREN expression RPAREN
                                    | constant
                                    | string
                                    | variable
        """
        token = self.current_token
        if token.type == LPAREN:
            self.eat(LPAREN)
            node = self.expression()
            self.eat(RPAREN)
            return node
        elif token.type in (INTEGER_CONST, REAL_CONST, CHAR_CONST):
            return self.constant()
        elif token.type == STRING:
            return self.string()
        else:
            return self.variable()

    def constant(self):
        """
        constant                    : INTEGER_CONST
                                    | REAL_CONST
                                    | CHAR_CONST
        """
        token = self.current_token
        if token.type == CHAR_CONST:
            self.eat(CHAR_CONST)
            return Num(
                token=token,
                line=self.lexer.line
            )
        elif token.type == INTEGER_CONST:
            self.eat(INTEGER_CONST)
            return Num(
                token=token,
                line=self.lexer.line
            )
        elif token.type == REAL_CONST:
            self.eat(REAL_CONST)
            return Num(
                token=token,
                line=self.lexer.line
            )

    def type_spec(self):
        """
        type_spec                   : TYPE
        """
        token = self.current_token
        if token.type in (CHAR, INT, FLOAT, DOUBLE,STR_TYPE):
            self.eat(token.type)
            return Type(
                token=token,
                line=self.lexer.line
            )

    def variable(self):
        """
        variable                    : ID
        """
        node = Var(
            token=self.current_token,
            line=self.lexer.line
        )
        self.eat(ID)
        return node

    def empty(self):
        """An empty production"""
        return NoOp(
            line=self.lexer.line
        )

    def string(self):
        """
        string                      : STRING
        """
        token = self.current_token
        self.eat(STRING)
        return String(
            token=token,
            line=self.lexer.line
        )

    def parse(self):
        """
        program                     : declarations

        declarations                : (include_library | function_declaration | declaration_list)*

        include_library             : HASH ID<'include'> LESS_THAN ID DOT ID<'h'> GREATER_THAN

        function_declaration        : type_spec ID LPAREN parameters RPAREN compound_statement

        function_body               : LBRACKET (declaration_list | statement)* RBRACKET

        parameters                  : type_spec variable (COMMA type_spec variable)*

        declaration_list            : declaration+

        declaration                 : type_spec init_declarator_list SEMICOLON

        init_declarator_list        : init_declarator (COMMA init_declarator)*

        init_declarator             : variable (ASSIGN assignment_expression)?

        statement                   : iteration_statement
                                    | selection_statement
                                    | jump_statement
                                    | compound_statement
                                    | expression_statement

        compound_statement          : LBRACKET (declaration_list | statement)* RBRACKET

        jump_statement              : RETURN expression? SEMICOLON
                                    | BREAK SEMICOLON
                                    | CONTINUE SEMICOLON

        selection_statement         : IF LPAREN expression RPAREN statement (ELSE statement)?

        iteration_statement         : WHILE LPAREN expression RPAREN statement
                                    | DO statement WHILE LPAREN expression RPAREN SEMICOLON
                                    | FOR LPAREN expression_statement expression_statement (expression)? RPAREN statement

        expression_statement        : expression* SEMICOLON

        constant_expression         : conditional_expression

        expression                  : assignment_expression (COMMA assignment_expression)*

        assignment_expression       : assignment_expression (COMMA assignment_expression)*
                                    | conditional_expression

        conditional_expression      : logical_and_expression (QUESTION_MARK expression COLON conditional_expression)?

        logical_and_expression      : logical_or_expression (LOG_AND_OP logical_or_expression)*

        logical_or_expression       : inclusive_or_expression (LOG_OR_OP inclusive_or_expression)*

        inclusive_or_expression     : exclusive_or_expression (OR_OP exclusive_or_expression)*

        exclusive_or_expression     : and_expression (XOR_OP and_expression)*

        and_expression              : equality_expression (AND_OP equality_expression)*

        equality_expression         : relational_expression ((EQ_OP | NE_OP) relational_expression)*

        relational_expression       : shift_expression ((LE_OP | LT_OP | GE_OP | GT_OP) shift_expression)*

        shift_expression            : additive_expression ((LEFT_OP | RIGHT_OP) additive_expression)*

        additive_expression         : multiplicative_expression ((ADD_OP | SUB_OP) multiplicative_expression)*

        multiplicative_expression   : cast_expression ((MUL_OP | DIV_OP | MOD_OP) cast_expression)*

        cast_expression             : LPAREN type_spec RPAREN cast_expression
                                    | unary_expression

        unary_expression            : INC_OP unary_expression
                                    | DEC_OP unary_expression
                                    | AND_OP cast_expression
                                    | ADD_OP cast_expression
                                    | SUB_OP cast_expression
                                    | LOG_NEG cast_expression
                                    | postfix_expression

        unary_expression            : primary_expression INC_OP
                                    | primary_expression DEC_OP
                                    | primary_expression LPAREN argument_expression_list? RPAREN

        argument_expression_list    : assignment_expression (COMMA assignment_expression)*

        primary_expression          : LPAREN expression RPAREN
                                    | constant
                                    | string
                                    | variable

        constant                    : INTEGER_CONST
                                    | REAL_CONST

        type_spec                   : TYPE

        variable                    : ID

        string                      : STRING

        """
        node = self.program()
        if self.current_token.type != EOF:
            self.error("Expected token <EOF> but found <{}>".format(self.current_token.type))

        return node
