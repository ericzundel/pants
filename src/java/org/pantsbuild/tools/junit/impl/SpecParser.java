package org.pantsbuild.tools.junit.impl;

import com.google.common.base.Preconditions;
import com.google.common.collect.ImmutableList;
import java.lang.reflect.Method;
import java.util.Collection;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Takes strings passed to the command line representing packages or individual methods
 * and returns a parsed Spec.  Each Spec represents a single class, so individual methods
 * are added into each spec
 */
public class SpecParser {
  private final Iterable<String> testSpecStrings;
  private Map<Class<?>, Spec> specs = new LinkedHashMap<Class<?>, Spec>();

  /**
   * Parses the list of incoming test specs from the command line.
   * <p>
   * Expects a list of string specs which can be represented as one of:
   * <ul>
   *   <li>package.className</li>
   *   <li>package.className#methodName</li>
   * </ul>
   * Note that each class or method will only be executed once, no matter how many times it is
   * present in the list.
   * </p>
   * <p>
   * It is illegal to pass a spec with just the className if there are also individual methods
   * present in the list within the same class.
   * </p>
   */
  // TODO(zundel): This could easily be extended to allow a regular expression in the spec
  public SpecParser(Collection<String> testSpecStrings) {
    Preconditions.checkArgument(!testSpecStrings.isEmpty());
    this.testSpecStrings = testSpecStrings;
  }

  /**
   * Parse the specs passed in to the constructor.
   * @return List of parsed specs
   * @throws SpecException
   */
  public List<Spec> parse() throws SpecException {
    for (String specString : testSpecStrings) {
      if (specString.indexOf('#') >= 0) {
        addMethod(specString);
        continue;
      }
      // The spec name is expected to be the same as the fully qualified class name
      if (specs.containsKey(specString)) {
        Spec spec = getOrCreateSpec(specString, specString);
        if (!spec.getMethods().isEmpty()) {
          throw new SpecException(specString,
              "Request for entire class already requesting individual methods");
        }
        continue;
      }
      getOrCreateSpec(specString, specString);
    }
    return ImmutableList.copyOf(specs.values());
  }

  private Spec getOrCreateSpec(String specString, String className) throws SpecException {
    try {
      Class<?> clazz = getClass().getClassLoader().loadClass(className);
      if(!specs.containsKey(clazz)) {
        specs.put(clazz, new Spec(clazz));
      }
      return specs.get(clazz);
    } catch (ClassNotFoundException e) {
      throw new SpecException(specString,
          String.format("Class %s not found in classpath.", className), e);
    } catch (NoClassDefFoundError e) {
      throw new SpecException(specString,
          String.format("Class %s not found in classpath.", className), e);
    } catch (LinkageError e) {
      // Any of a number of runtime linking errors can occur when trying to load a class,
      // fail with the test spec so the class failing to link is known.
      throw new SpecException(specString,
          String.format("Error linking %s.", className), e);
      // See the comment below for justification.
    } catch (RuntimeException e) {
      // The class may fail with some variant of RTE in its static initializers, trap these
      // and dump the bad spec in question to help narrow down issue.
      throw new SpecException(specString,
          String.format("Error initializing %s.",className), e);
    }
  }

  /**
   * Handle a spec that looks like package.className#methodName
   */
  public void addMethod(String specString) throws SpecException {
    String[] results = specString.split("#");
    if (results.length != 2) {
      throw new SpecException(specString, "Expected only one # in spec");
    }
    String className = results[0];
    String methodName = results[1];

    Spec spec = getOrCreateSpec(specString, className);
    boolean found = false;
    for (Method clazzMethod : spec.getSpecClass().getMethods()) {
      if (clazzMethod.getName().equals(methodName)) {
        found = true;
        break;
      }
    }
    if (!found) {
      throw new SpecException(specString,
          String.format("Method %s not found in class %s", methodName, className));
    }
    spec.addMethod(methodName);
  }
}
