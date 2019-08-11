package actions;

import java.io.DataOutputStream;
import java.net.Socket;

import javafx.event.ActionEvent;
import javafx.event.EventHandler;
import view.MainScreen;

public class SendAction implements EventHandler<ActionEvent> {

	@Override
	public void handle(ActionEvent arg0) {
		String str = MainScreen.get().console.field.getText();

		if (str.isEmpty())
			return;

		try {

			Socket soc = new Socket("localhost", 5001);
			DataOutputStream dout = new DataOutputStream(soc.getOutputStream());
			dout.writeUTF(":" + str);
			dout.flush();
			dout.close();
			soc.close();

		} catch (Exception e) {
			System.out.println("Client FAIL");
		}
	}

}
