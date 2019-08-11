package actions;

import interpreter.Interpreter;
import javafx.event.ActionEvent;
import javafx.event.EventHandler;
import view.MainScreen;

public class CheckAction implements EventHandler<ActionEvent> {

	@Override
	public void handle(ActionEvent arg0) {
		String program = MainScreen.get().editor.getInput().getText();

		MainScreen.get().interpreter.checkPy(program);

	}

}
