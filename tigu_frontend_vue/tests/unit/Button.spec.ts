import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import Button from '@/components/common/Button.vue';

describe('Button.vue', () => {
  it('renders slot content', () => {
    const wrapper = mount(Button, {
      slots: {
        default: 'Test Button'
      }
    });
    expect(wrapper.text()).toContain('Test Button');
  });

  it('applies variant class', () => {
    const wrapper = mount(Button, {
      props: {
        variant: 'danger'
      }
    });
    expect(wrapper.classes()).toContain('btn-danger');
  });

  it('disables button when disabled prop is true', () => {
    const wrapper = mount(Button, {
      props: {
        disabled: true
      }
    });
    expect(wrapper.attributes('disabled')).toBeDefined();
  });

  it('shows loading spinner when loading prop is true', () => {
    const wrapper = mount(Button, {
      props: {
        loading: true
      }
    });
    expect(wrapper.find('.spinner').exists()).toBe(true);
  });

  it('emits click event when clicked', async () => {
    const wrapper = mount(Button);
    await wrapper.trigger('click');
    expect(wrapper.emitted('click')).toBeTruthy();
  });

  it('does not emit click event when disabled', async () => {
    const wrapper = mount(Button, {
      props: {
        disabled: true
      }
    });
    await wrapper.trigger('click');
    expect(wrapper.emitted('click')).toBeFalsy();
  });
});
