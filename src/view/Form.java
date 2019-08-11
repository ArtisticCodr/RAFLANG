package view;

import javafx.scene.Scene;
import javafx.scene.image.Image;
import javafx.scene.layout.Pane;
import javafx.stage.Stage;
import javafx.stage.WindowEvent;

public class Form extends Stage {

	public Form(String title) {
		this(title, null);
	}

	public Form(String title, Pane pane) {
		setTitle(title);
		setOnCloseRequest((WindowEvent we) -> {
			onClose();
		});
		if (pane != null) {
			setPane(pane);
			show();
		}

		getIcons().add(new Image("/assets/icon.png"));
	}

	public Pane getPane() {
		return (Pane) getScene().getRoot();
	}

	public void setPane(Pane pane) {
		Scene scene = new Scene(pane);
		scene.getStylesheets().add(Form.class.getResource("/design.css").toExternalForm());
		setScene(scene);
		if (!isShowing())
			show();
	}

	protected void onClose() {

	}

	@Override
	public final void close() {
		getOnCloseRequest().handle(null);
		super.close();
	}

}
