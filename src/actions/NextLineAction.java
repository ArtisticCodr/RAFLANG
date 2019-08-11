package actions;

import java.io.DataOutputStream;
import java.net.Socket;

import javafx.event.ActionEvent;
import javafx.event.EventHandler;

public class NextLineAction implements EventHandler<ActionEvent> {

	@Override
	public void handle(ActionEvent arg0) {
		try {

			Socket soc = new Socket("localhost", 7000);
			DataOutputStream dout = new DataOutputStream(soc.getOutputStream());
			dout.writeUTF("next");
			dout.flush();
			dout.close();
			soc.close();

		} catch (Exception e) {
			System.out.println("ClientNextLine FAIL");
		}
	}

}