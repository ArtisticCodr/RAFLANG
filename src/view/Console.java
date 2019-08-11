package view;

import java.util.ArrayList;

import org.fxmisc.flowless.VirtualizedScrollPane;
import org.fxmisc.richtext.StyleClassedTextArea;

import actions.SendAction;
import javafx.event.EventHandler;
import javafx.geometry.Insets;
import javafx.scene.control.Button;
import javafx.scene.control.Tab;
import javafx.scene.control.TextField;
import javafx.scene.input.KeyCode;
import javafx.scene.input.KeyEvent;
import javafx.scene.layout.BorderPane;
import javafx.scene.layout.GridPane;
import javafx.scene.layout.Priority;

public class Console extends Tab {

	public StyleClassedTextArea output = new StyleClassedTextArea();
	public TextField field = new TextField();
	public Button send = new Button("Send");
	
	public Console() {	
		output.setFocusTraversable(false);
		output.setPadding(new Insets(-1,10,10,0));
		output.setPrefWidth(250);
		output.setId("console");
		output.setEditable(false);
		output.setOnKeyPressed(new EventHandler<KeyEvent>() {

			@Override
			public void handle(KeyEvent event) {
				if (event.getCode() == KeyCode.DELETE) {
                    output.clear();
                }
				
			}
		});
		
		output.setStyle("-fx-font-size: 15px;");
		
		
		BorderPane p1 = new BorderPane();
		p1.setStyle("-fx-background-color: #afd0ff;");
		p1.setPadding(new Insets(0,5,5,1));
		
		p1.setCenter(new VirtualizedScrollPane<>(output));
		GridPane gp = new GridPane();
		field.setMinWidth(100);
		gp.add(field, 0, 0);
		gp.add(send, 1, 0);
		p1.setBottom(gp);
		gp.setHgrow(field, Priority.ALWAYS);
		send.setOnAction(new SendAction());
		
		setContent(p1);
		setText("Console");
	}

}
