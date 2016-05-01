package org.pantsbuild.tools.junit.impl;

import org.pantsbuild.junit.annotations.TestParallel;
import org.pantsbuild.junit.annotations.TestSerial;

/**
 * Tests the annotation override behavior.
 * {@link TestSerial} should override all other annotations.
 */
@TestParallel
@TestSerial
public class AnnotationOverrideClass {
}
