package interpreter;

import java.io.BufferedReader;
import java.io.File;
import java.io.PrintWriter;

public class PyExecuter extends Thread {

	String program;
	int run;

	public PyExecuter(String program, int run) {
		this.program = program;
		this.run = run;
	}

	@Override
	public void run() {
		try {
			BufferedReader in = null;
			File f = new File("Interpreter/input.txt");
			PrintWriter pw = new PrintWriter(f);
			pw.print(program);
			pw.close();
			String exStr = "";

			if (run == 1)
				exStr = "python Interpreter/__main__.py ";
			if (run == 2)
				exStr = "python Interpreter/__main__1.py ";
			if (run == 3)
				exStr = "python Interpreter/__main__3.py ";

			Process p = Runtime.getRuntime().exec(exStr);

		} catch (Exception e) {
			e.printStackTrace();
		}
	}
}
