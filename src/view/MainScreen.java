package view;

import org.fxmisc.flowless.VirtualizedScrollPane;

import actions.CheckAction;
import actions.DebugAction;
import actions.NextLineAction;
import actions.RunAction;
import interpreter.CloseCilent;
import interpreter.Interpreter;
import javafx.geometry.Insets;
import javafx.geometry.Orientation;
import javafx.geometry.Pos;
import javafx.scene.control.Button;
import javafx.scene.control.Separator;
import javafx.scene.control.SplitPane;
import javafx.scene.control.TabPane;
import javafx.scene.control.TabPane.TabClosingPolicy;
import javafx.scene.control.TextField;
import javafx.scene.control.ToolBar;
import javafx.scene.layout.BorderPane;

public class MainScreen extends Form {

	private static MainScreen instance = null;
	public Interpreter interpreter = new Interpreter();

	public Button check = new Button();
	public Button run = new Button();
	public Button debug = new Button();
	public Button nextLine = new Button();

	public Editor editor = new Editor();
	public Console console;
	public Stack stack;
	public TextField debugField;
	public volatile boolean isWaiting = false;
	
	public static MainScreen get() {
		if (instance == null)
			new MainScreen();
		return instance;
	}

	public MainScreen() {
		super("RAFLANG");
		instance = this;
		setWidth(900);
		setHeight(600);


		check.setStyle("-fx-graphic: url('/assets/check.png');");
		run.setStyle("-fx-graphic: url('/assets/run.png');");
		debug.setStyle("-fx-graphic: url('/assets/debug.png');");
		nextLine.setStyle("-fx-graphic: url('/assets/nextLine.png');");
		
		check.setOnAction(new CheckAction());
		run.setOnAction(new RunAction());
		nextLine.setOnAction(new NextLineAction());
		

		Separator sep = new Separator();
		sep.setPadding(new Insets(0,0,0,10));
		ToolBar toolbar = new ToolBar();
		debugField = new TextField();
		debugField.setMaxWidth(40);
		debugField.setAlignment(Pos.CENTER);
		toolbar.getItems().addAll(new Separator(), check, run, sep, debug, nextLine, debugField);
		
		
		
		debug.setOnAction(new DebugAction());
		
		console = new Console();
		stack = new Stack();

		TabPane TP = new TabPane(console, stack);
		TP.setTabClosingPolicy(TabClosingPolicy.UNAVAILABLE);
		
		
		BorderPane bPane = new BorderPane();
		bPane.setTop(toolbar);
		
		BorderPane p = new BorderPane();
		p.setStyle("-fx-background-color: #afd0ff;");
		p.setPadding(new Insets(35,10,5,5));
		
		p.setCenter((new VirtualizedScrollPane<>(editor.getInput())));
		p.setMinWidth(500);
		
		
		SplitPane splitPane = new SplitPane();
		splitPane.setOrientation(Orientation.HORIZONTAL);
		splitPane.getItems().add(p);
		splitPane.getItems().add(TP);
		
		splitPane.setStyle("-fx-box-border: #afd0ff;");
		
		bPane.setCenter(splitPane);
		
		bPane.setFocusTraversable(false);
		bPane.setStyle("-fx-background-color: #afd0ff;");
		
		setOnCloseRequest(new CloseCilent());
		
		setPane(bPane);
	}

}
