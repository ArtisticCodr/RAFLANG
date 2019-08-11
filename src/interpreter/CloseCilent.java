package interpreter;

import java.io.DataOutputStream;
import java.net.Socket;

import javafx.event.EventHandler;
import javafx.stage.WindowEvent;

public class CloseCilent implements EventHandler<WindowEvent> {

	public void closeConsoleServer() {
		try {
			Socket soc = new Socket("localhost", 5000);
			DataOutputStream dout = new DataOutputStream(soc.getOutputStream());
			dout.writeUTF("$exit$");
			dout.flush();
			dout.close();
			soc.close();

		} catch (Exception e) {
			//e.printStackTrace();
		}
	}
	
	public void closeStackServer() {
		try {
			Socket soc = new Socket("localhost", 6000);
			DataOutputStream dout = new DataOutputStream(soc.getOutputStream());
			dout.writeUTF("$exit$");
			dout.flush();
			dout.close();
			soc.close();

		} catch (Exception e) {
			//e.printStackTrace();
		}
	}

	
	public void closePyServer() {
		try {
			Socket soc = new Socket("localhost", 5001);
			DataOutputStream dout = new DataOutputStream(soc.getOutputStream());
			dout.writeUTF("$exit$");
			dout.flush();
			dout.close();
			soc.close();

		} catch (Exception e) {
			//e.printStackTrace();
		}
	}
	
	public void closePyDebugServer() {
		try {
			Socket soc = new Socket("localhost", 7000);
			DataOutputStream dout = new DataOutputStream(soc.getOutputStream());
			dout.writeUTF("$exit$");
			dout.flush();
			dout.close();
			soc.close();

		} catch (Exception e) {
			//e.printStackTrace();
		}
	}

	@Override
	public void handle(WindowEvent event) {
		closeConsoleServer();
		closeStackServer();
		closePyServer();
		closePyDebugServer();
	}

}
