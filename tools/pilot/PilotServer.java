// Persistent SysML v2 Pilot Implementation validator (SysMLInteractive), for use inside a repair loop.
// Usage: java -cp <jupyter-sysml-kernel-*-all.jar>:<dir of this class> PilotServer <sysml.library dir>
// Protocol (stdin/stdout, UTF-8): the client writes the absolute path of a .sysml file per line; the server
// validates it in its own resource (removed afterwards) and answers one line per issue
//   kind <TAB> severity <TAB> code <TAB> line <TAB> column <TAB> message
// (kind = SYNTAX | ISSUE | EXCEPTION) followed by a line "DONE". It prints "READY" once the library is loaded.
import org.eclipse.xtext.validation.Issue;
import org.omg.sysml.interactive.SysMLInteractive;
import org.omg.sysml.interactive.SysMLInteractiveResult;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.HashSet;
import java.util.Set;

public class PilotServer {
    static String clean(String s) {
        return s == null ? "" : s.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ');
    }

    public static void main(String[] args) throws Exception {
        PrintStream out = new PrintStream(new java.io.FileOutputStream(java.io.FileDescriptor.out), true, "UTF-8");
        System.setOut(new PrintStream(java.io.OutputStream.nullOutputStream()));  // library loading logs
        SysMLInteractive sysml = SysMLInteractive.getInstance();
        sysml.loadLibrary(args[0]);
        out.println("READY");
        BufferedReader in = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8));
        String path;
        while ((path = in.readLine()) != null) {
            path = path.trim();
            if (path.isEmpty()) {
                continue;
            }
            StringBuilder answer = new StringBuilder();
            try {
                SysMLInteractiveResult result = sysml.process(Files.readString(Paths.get(path)));
                if (result.getException() != null) {
                    answer.append("EXCEPTION\t\t\t\t\t").append(clean(result.getException().toString())).append('\n');
                } else {
                    Set<Issue> syntax = new HashSet<>(result.getSyntaxErrors());
                    for (Issue issue : result.getIssues()) {
                        answer.append(syntax.contains(issue) ? "SYNTAX" : "ISSUE").append('\t')
                              .append(issue.getSeverity()).append('\t').append(clean(issue.getCode())).append('\t')
                              .append(issue.getLineNumber()).append('\t').append(issue.getColumn()).append('\t')
                              .append(clean(issue.getMessage())).append('\n');
                    }
                }
            } catch (Throwable t) {
                answer.append("EXCEPTION\t\t\t\t\t").append(clean(t.toString())).append('\n');
            } finally {
                sysml.removeResource();
            }
            out.print(answer);
            out.println("DONE");
        }
    }
}
