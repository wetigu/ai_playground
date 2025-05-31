import { describe, it, expect } from 'vitest';
import HelloWorld from '@/components/HelloWorld.vue';

describe('HelloWorld.vue', () => {
  it('renders properly', () => {
    const wrapper = mount(HelloWorld);
    expect(wrapper.text()).toContain('Hello World');
  });
});