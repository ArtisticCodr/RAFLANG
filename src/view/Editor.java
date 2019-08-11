package view;

import java.time.Duration;
import java.util.Collection;
import java.util.Collections;
import java.util.Optional;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.fxmisc.richtext.CodeArea;
import org.fxmisc.richtext.LineNumberFactory;
import org.fxmisc.richtext.model.StyleSpans;
import org.fxmisc.richtext.model.StyleSpansBuilder;

import javafx.concurrent.Task;

public class Editor {

	CodeArea input = new CodeArea();
	private ExecutorService executor;

	public Editor() {
		executor = Executors.newSingleThreadExecutor();

		input.setStyle("-fx-font-size: 15px;");
		input.setFocusTraversable(false);
		input.setWrapText(true);
		input.setId("input");

		input.setParagraphGraphicFactory(LineNumberFactory.get(input));
		input.richChanges().filter(ch -> !ch.getInserted().equals(ch.getRemoved())) // XXX
				.successionEnds(Duration.ofMillis(100)).supplyTask(this::computeHighlightingAsync)
				.awaitLatest(input.richChanges()).filterMap(t -> {
					if (t.isSuccess()) {
						return Optional.of(t.get());
					} else {
						t.getFailure().printStackTrace();
						return Optional.empty();
					}
				}).subscribe(this::applyHighlighting);
	}

	public CodeArea getInput() {
		return input;
	}

	public void setInput(CodeArea input) {
		this.input = input;
	}

	private Task<StyleSpans<Collection<String>>> computeHighlightingAsync() {
		String text = input.getText();
		Task<StyleSpans<Collection<String>>> task = new Task<StyleSpans<Collection<String>>>() {
			@Override
			protected StyleSpans<Collection<String>> call() throws Exception {
				return computeHighlighting(text);
			}
		};
		executor.execute(task);
		return task;
	}

	private void applyHighlighting(StyleSpans<Collection<String>> highlighting) {
		input.setStyleSpans(0, highlighting);
	}

	private static StyleSpans<Collection<String>> computeHighlighting(String text) {
		Matcher matcher = PATTERN.matcher(text);
		int lastKwEnd = 0;
		StyleSpansBuilder<Collection<String>> spansBuilder = new StyleSpansBuilder<>();
		while (matcher.find()) {
			String styleClass = matcher.group("KEYWORD") != null ? "keyword"
					: matcher.group("PAREN") != null ? "paren"
							: matcher.group("BRACE") != null ? "brace"
									: matcher.group("BRACKET") != null ? "bracket"
											: matcher.group("SEMICOLON") != null ? "semicolon"
													: matcher.group("STRING") != null ? "string"
															: matcher.group("VARIABLE") != null ? "comment" : null;
			/* never happens */ assert styleClass != null;
			spansBuilder.add(Collections.emptyList(), matcher.start() - lastKwEnd);
			spansBuilder.add(Collections.singleton(styleClass), matcher.end() - matcher.start());
			lastKwEnd = matcher.end();
		}
		spansBuilder.add(Collections.emptyList(), text.length() - lastKwEnd);
		return spansBuilder.create();
	}

	private static final String[] KEYWORDS = new String[] { "toscreen", "inject", "fromscreen", "give", "skiprest",
			"if", "fi", "fifi", "from", "repeatto", "while", "elihw", "do", "bb", "func", "cunf", "learn" };

	private static final String[] VARIABLES = new String[] { "\\[\\*\\]", "\\[\\+\\]", "\\[\\+\\.\\+\\]",
			"\\[\\~\\]" }; // ovo koristimo kao repr variabli

	private static final String KEYWORD_PATTERN = "\\b(" + String.join("|", KEYWORDS) + ")\\b";
	private static final String PAREN_PATTERN = "\\(|\\)";
	private static final String BRACE_PATTERN = "\\{|\\}";
	private static final String BRACKET_PATTERN = "\\[|\\]";
	private static final String SEMICOLON_PATTERN = "\\;";
	private static final String STRING_PATTERN = "\"([^\"\\\\]|\\\\.)*\"";
	private static final String VARIABLES_PATTERN = "(" + String.join("|", VARIABLES) + ")";

	private static final Pattern PATTERN = Pattern.compile(
			"(?<KEYWORD>" + KEYWORD_PATTERN + ")" + "|(?<PAREN>" + PAREN_PATTERN + ")" + "|(?<BRACE>" + BRACE_PATTERN
					+ ")" + "|(?<VARIABLE>" + VARIABLES_PATTERN + ")" + "|(?<SEMICOLON>" + SEMICOLON_PATTERN + ")"
					+ "|(?<STRING>" + STRING_PATTERN + ")" + "|(?<BRACKET>" + BRACKET_PATTERN + ")");

}
