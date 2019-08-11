package interpreter;

import actions.NextLineAction;
import view.MainScreen;

public class Interpreter {
	public volatile boolean newMessage = false;
	public volatile String message = "";

	public Interpreter() {
		// pravimo server
		ConsoleServer consoleServer = new ConsoleServer(this);
		consoleServer.start();

		StackServer stackServer = new StackServer(this);
		stackServer.start();
	}

	public void checkPy(String program) {
		if (program.isEmpty())
			return;
		PyExecuter ex = new PyExecuter(program, 1);
		ex.start();

		System.out.println("interpreter finish");
	}

	public void runPy(String program) {
		PyExecuter ex = new PyExecuter(program, 2);
		ex.start();

		System.out.println("interpreter finish");
	}

	public void debugPy(String program, int line) {
		PyExecuter ex = new PyExecuter(program, 3);
		ex.start();
		
		NextLineAction nl = new NextLineAction();
		for(int i = 1; i<line; i++) {
			waiting();
			nl.handle(null);
		}

		System.out.println("interpreter finish");
	}

	public static void ErrorToConsole(String message) {
		if (message.equals(""))
			return;
		int begin = MainScreen.get().console.output.getLength();
		message += '\n';
		int end = begin + message.length();

		MainScreen.get().console.output.appendText(message);
		MainScreen.get().console.output.setStyleClass(begin, end, "red");
		MainScreen.get().console.output.setStyleClass(end, end, "black");
	}

	public static void MessageToConsole(String message) {
		if (message.equals(""))
			return;
		int begin = MainScreen.get().console.output.getLength();
		message = message.replace("\\n", "\n");
		int end = begin + message.length();

		MainScreen.get().console.output.appendText(message);
		MainScreen.get().console.output.setStyleClass(begin, end, "green");
		MainScreen.get().console.output.setStyleClass(end, end, "black");
	}

	public static void MessageToStack(String message) {
		if (message.equals(""))
			return;

		message = message.replace(":int", ":[+]");
		message = message.replace(":char", ":[*]");
		message = message.replace(":float", ":[+.+]");
		message = message.replace(":double", ":[+.+]");

		int begin = MainScreen.get().stack.output.getLength();
		message = message.replace("\\n", "\n");
		int end = begin + message.length();

		MainScreen.get().stack.output.appendText(message);
		MainScreen.get().stack.output.setStyleClass(begin, end, "blue");
		MainScreen.get().stack.output.setStyleClass(end, end, "blue");
	}

	public static void ClearStack() {
		MainScreen.get().stack.output.clear();
	}

	
	public void waiting() {
		boolean waiting = MainScreen.get().isWaiting;
		while(!waiting)
			waiting = MainScreen.get().isWaiting;
		
		MainScreen.get().isWaiting = false;
	}
}
