package interpreter;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.ServerSocket;
import java.net.Socket;

import javafx.application.Platform;
import view.MainScreen;

public class StackServer extends Thread {

	Interpreter interpreter;

	public StackServer(Interpreter interpreter) {
		this.interpreter = interpreter;
		setDaemon(true);
	}

	@Override
	public void run() {

		try {
			System.out.println("Stack server is started");
			ServerSocket serverSocket = new ServerSocket(6000);
			System.out.println("Stack server is waiting");
			Socket socket;

			while (true) {
				socket = serverSocket.accept();
				BufferedReader reader = new BufferedReader(new InputStreamReader(socket.getInputStream()));
				String str = reader.readLine();

				if (str.contains("$exit$")) {
					socket.close();
					reader.close();
					serverSocket.close();
					break;
				}
				
				if (str.contains("$waiting$")) {
					socket.close();
					reader.close();
					MainScreen.get().isWaiting = true;
					continue;
				}

				StringBuilder sb = new StringBuilder();
				while (str != null) {
					sb.append(str + '\n');
					str = reader.readLine();
				}

				Platform.runLater(new Runnable() {
					@Override
					public void run() {

						interpreter.ClearStack();
						interpreter.MessageToStack(sb.toString());

					}
				});

			}

		} catch (Exception e) {
			// e.printStackTrace();
		}

	}

}