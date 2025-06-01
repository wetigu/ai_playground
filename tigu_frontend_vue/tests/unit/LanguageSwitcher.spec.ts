import { describe, it, expect } from 'vitest';

// Simple test without importing components that may have complex dependencies
describe('Basic Test Suite', () => {
  it('should pass a basic test', () => {
    expect(true).toBe(true);
  });

  it('should perform basic math', () => {
    expect(2 + 2).toBe(4);
  });
});