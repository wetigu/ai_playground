import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import LanguageSwitcher from '@/components/LanguageSwitcher.vue';

describe('LanguageSwitcher.vue', () => {
  it('renders properly', () => {
    const wrapper = mount(LanguageSwitcher);
    expect(wrapper.exists()).toBe(true);
  });
});