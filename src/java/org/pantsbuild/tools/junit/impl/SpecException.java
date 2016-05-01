package org.pantsbuild.tools.junit.impl;

public class SpecException extends Exception {

  public SpecException(String spec, String message) {
    super(formatMessage(spec, message));
  }

  public SpecException(String spec, String message, Throwable t) {
    super(formatMessage(spec, message), t);
  }

  private static String formatMessage(String spec, String message) {
    return String.format("FATAL: Error parsing spec %s: %s",spec, message);
  }
}
