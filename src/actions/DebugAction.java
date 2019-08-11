package actions;

import javafx.event.ActionEvent;
import javafx.event.EventHandler;
import view.MainScreen;

public class DebugAction implements EventHandler<ActionEvent> {

	@Override
	public void handle(ActionEvent arg0) {
		String program = MainScreen.get().editor.getInput().getText();
		int line;
		try {
			line = Integer.parseInt(MainScreen.get().debugField.getText());
		} catch (Exception e) {
			return;
		}

		MainScreen.get().interpreter.debugPy(program, line);

	}

}