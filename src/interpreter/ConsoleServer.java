package interpreter;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.ServerSocket;
import java.net.Socket;

import javafx.application.Platform;
import view.MainScreen;

public class ConsoleServer extends Thread {

	Interpreter interpreter;
	Socket socket;
	ServerSocket serverSocket;

	public ConsoleServer(Interpreter interpreter) {
		this.interpreter = interpreter;
		setDaemon(true);
	}

	@Override
	public void run() {

		try {
			System.out.println("Console server is started");
			serverSocket = new ServerSocket(5000);
			System.out.println("Console server is waiting");
		} catch (Exception e) {

		}

		while (true) {
			try {

				socket = serverSocket.accept();
				BufferedReader reader = new BufferedReader(new InputStreamReader(socket.getInputStream()));
				String str = reader.readLine();

				if (str.contains("$exit$")) {
					socket.close();
					reader.close();
					serverSocket.close();
					break;
				}

				StringBuilder sb = new StringBuilder();
				while (str != null) {
					sb.append(str);
					str = reader.readLine();
				}

				Platform.runLater(new Runnable() {
					@Override
					public void run() {

						if (sb.toString().contains("ERROR"))
							interpreter.ErrorToConsole(sb.toString());
						else
							interpreter.MessageToConsole(sb.toString());

					}
				});

			} catch (Exception e) {
				//e.printStackTrace();
			}
		}

	}

}
