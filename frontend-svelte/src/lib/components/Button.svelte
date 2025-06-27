<script>
  import Loading from './Loading.svelte';
  
  // Props
  export let variant = 'primary'; // primary, secondary, outline, danger
  export let size = 'md'; // sm, md, lg
  export let loading = false;
  export let disabled = false;
  export let type = 'button';
  export let href = null;
  export let target = null;
  export let fullWidth = false;
  export let icon = null;
  export let iconPosition = 'left'; // left, right
  
  // Component to use (button or a)
  $: component = href ? 'a' : 'button';
  
  // Class combinations
  $: baseClasses = [
    'inline-flex items-center justify-center font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed',
    fullWidth ? 'w-full' : '',
    getVariantClasses(variant),
    getSizeClasses(size)
  ].filter(Boolean).join(' ');
  
  function getVariantClasses(variant) {
    const variants = {
      primary: 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 focus:ring-blue-500 shadow-lg hover:shadow-xl transform hover:scale-105',
      secondary: 'bg-gradient-to-r from-green-600 to-emerald-600 text-white hover:from-green-700 hover:to-emerald-700 focus:ring-green-500 shadow-lg hover:shadow-xl transform hover:scale-105',
      outline: 'border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 hover:border-blue-500 hover:text-blue-600 focus:ring-blue-500',
      danger: 'bg-gradient-to-r from-red-600 to-pink-600 text-white hover:from-red-700 hover:to-pink-700 focus:ring-red-500 shadow-lg hover:shadow-xl transform hover:scale-105',
      ghost: 'text-gray-600 hover:text-blue-600 hover:bg-blue-50 focus:ring-blue-500'
    };
    return variants[variant] || variants.primary;
  }
  
  function getSizeClasses(size) {
    const sizes = {
      sm: 'px-3 py-2 text-sm rounded-lg gap-1.5',
      md: 'px-6 py-3 text-base rounded-xl gap-2',
      lg: 'px-8 py-4 text-lg rounded-2xl gap-3'
    };
    return sizes[size] || sizes.md;
  }
</script>

<svelte:element 
  this={component}
  class={baseClasses}
  class:opacity-50={loading}
  class:cursor-not-allowed={disabled || loading}
  {type}
  {href}
  {target}
  disabled={disabled || loading}
  on:click
  on:keydown
  on:mouseenter
  on:mouseleave
  {...$$restProps}
>
  {#if loading}
    <Loading size="sm" />
  {:else if icon && iconPosition === 'left'}
    <span class="text-lg">{icon}</span>
  {/if}
  
  <slot />
  
  {#if !loading && icon && iconPosition === 'right'}
    <span class="text-lg">{icon}</span>
  {/if}
</svelte:element>

<style>
  /* Additional custom styles if needed */
</style>