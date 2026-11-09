// Batch validation of SysML v2 files with the SysML v2 Pilot Implementation (SysMLInteractive).
// Usage: java -cp <jupyter-sysml-kernel-*-all.jar>:<dir of this class> PilotBatch <sysml.library dir> <input dir> <output tsv>
// Every *.sysml file of <input dir> is parsed, linked and validated in its own resource (removed afterwards, so
// no model can resolve names against another one). Output: one line per issue and a DONE line per file:
//   id <TAB> kind <TAB> severity <TAB> code <TAB> line <TAB> message
// kind = SYNTAX (parser/lexer error), ISSUE (linking or validation issue), EXCEPTION or DONE.
import org.eclipse.xtext.validation.Issue;
import org.omg.sysml.interactive.SysMLInteractive;
import org.omg.sysml.interactive.SysMLInteractiveResult;

import java.io.BufferedWriter;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Stream;

public class PilotBatch {
    static String clean(String s) {
        return s == null ? "" : s.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ');
    }

    public static void main(String[] args) throws Exception {
        SysMLInteractive sysml = SysMLInteractive.getInstance();
        sysml.loadLibrary(args[0]);
        List<Path> files;
        try (Stream<Path> stream = Files.list(Paths.get(args[1]))) {
            files = stream.filter(p -> p.toString().endsWith(".sysml")).sorted().toList();
        }
        try (BufferedWriter out = Files.newBufferedWriter(Paths.get(args[2]))) {
            for (Path file : files) {
                String id = file.getFileName().toString().replaceAll("\\.sysml$", "");
                try {
                    SysMLInteractiveResult result = sysml.process(Files.readString(file));
                    if (result.getException() != null) {
                        out.write(id + "\tEXCEPTION\t\t\t\t" + clean(result.getException().toString()) + "\n");
                    } else {
                        Set<Issue> syntax = new HashSet<>(result.getSyntaxErrors());
                        for (Issue issue : result.getIssues()) {
                            out.write(id + "\t" + (syntax.contains(issue) ? "SYNTAX" : "ISSUE") + "\t" + issue.getSeverity()
                                    + "\t" + clean(issue.getCode()) + "\t" + issue.getLineNumber() + "\t"
                                    + clean(issue.getMessage()) + "\n");
                        }
                    }
                } catch (Throwable t) {
                    out.write(id + "\tEXCEPTION\t\t\t\t" + clean(t.toString()) + "\n");
                } finally {
                    sysml.removeResource();
                }
                out.write(id + "\tDONE\t\t\t\t\n");
                out.flush();
            }
        }
    }
}
