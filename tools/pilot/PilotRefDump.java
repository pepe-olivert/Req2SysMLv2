// Dump of the resolved cross references of SysML v2 files with the SysML v2 Pilot Implementation (SysMLInteractive).
// Usage: java -cp <jupyter-sysml-kernel-*-all.jar>:<dir of this class> PilotRefDump <sysml.library dir> <input dir> <output tsv>
// Every *.sysml file of <input dir> is parsed and linked in its own resource (removed afterwards). For every explicit
// (non-derived) cross reference written in the file, one line:
//   id <TAB> line <TAB> text <TAB> eclass <TAB> reference <TAB> chain <TAB> index <TAB> proxy <TAB> target qualified name
// text is the source text of the reference (e.g. A::x); for a FeatureChaining, chain identifies the chained feature and
// index the position of the link in the chain. A line "id DONE" closes each file.
import org.eclipse.emf.common.util.TreeIterator;
import org.eclipse.emf.ecore.EObject;
import org.eclipse.emf.ecore.EReference;
import org.eclipse.xtext.nodemodel.INode;
import org.eclipse.xtext.nodemodel.util.NodeModelUtils;
import org.omg.sysml.interactive.SysMLInteractive;
import org.omg.sysml.lang.sysml.Element;
import org.omg.sysml.lang.sysml.FeatureChaining;

import java.io.BufferedWriter;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.stream.Stream;

public class PilotRefDump {
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
                String id = file.getFileName().toString().replaceFirst("\\.sysml$", "");
                StringBuilder answer = new StringBuilder();
                try {
                    // The steps of process() without its removal of the resource, which release 2026-08 does when
                    // the model has errors; in 2026-08 next() takes the extension of the new resource.
                    String source = Files.readString(file);
                    try {
                        SysMLInteractive.class.getMethod("next", String.class).invoke(sysml, ".sysml");
                    } catch (NoSuchMethodException e) {
                        SysMLInteractive.class.getMethod("next").invoke(sysml);
                    }
                    sysml.parse(source);
                    sysml.validate();
                    TreeIterator<EObject> it = sysml.getResource().getAllContents();
                    while (it.hasNext()) {
                        EObject o = it.next();
                        String chain = "", index = "";
                        if (o instanceof FeatureChaining fc && fc.getFeatureChained() != null) {
                            chain = Integer.toString(System.identityHashCode(fc.getFeatureChained()));
                            index = Integer.toString(fc.getFeatureChained().getOwnedFeatureChaining().indexOf(fc));
                        }
                        for (EReference r : o.eClass().getEAllReferences()) {
                            if (r.isContainment() || r.isContainer() || r.isDerived() || r.isTransient() || r.isMany()) {
                                continue;
                            }
                            List<INode> nodes = NodeModelUtils.findNodesForFeature(o, r);
                            if (nodes.isEmpty()) {
                                continue;  // implied, not written in the file
                            }
                            StringBuilder text = new StringBuilder();
                            for (INode n : nodes) {
                                text.append(n.getText().trim());
                            }
                            EObject raw = (EObject) o.eGet(r, false);
                            EObject target = (EObject) o.eGet(r, true);
                            boolean proxy = target == null || target.eIsProxy();
                            String qn = !proxy && target instanceof Element e ? e.getQualifiedName() : "";
                            answer.append(id).append('\t').append(nodes.get(0).getStartLine()).append('\t')
                                  .append(clean(text.toString())).append('\t').append(o.eClass().getName()).append('\t')
                                  .append(r.getName()).append('\t').append(chain).append('\t').append(index).append('\t')
                                  .append(proxy || raw == null ? "1" : "0").append('\t').append(clean(qn)).append('\n');
                        }
                    }
                } catch (Throwable t) {
                    answer.append(id).append("\tEXCEPTION\t").append(clean(t.toString())).append('\n');
                } finally {
                    sysml.removeResource();
                }
                out.write(answer.toString());
                out.write(id + "\tDONE\n");
                out.flush();
            }
        }
    }
}
