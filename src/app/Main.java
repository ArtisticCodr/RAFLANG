package app;

import javafx.application.Application;
import javafx.stage.Stage;
import view.MainScreen;

public class Main extends Application {

	@Override
	public void start(Stage arg0) throws Exception {
		MainScreen.get();
	}

	public static void main(String[] args) {
		launch(args);
		System.out.println("Finished..");
	}

}
