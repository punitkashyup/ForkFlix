<script>
  import { createEventDispatcher } from 'svelte';
  import Button from './Button.svelte';
  
  const dispatch = createEventDispatcher();
  
  export let open = false;
  export let title = '';
  export let confirmText = 'Confirm';
  export let cancelText = 'Cancel';
  export let confirmVariant = 'primary';
  export let loading = false;
  export let size = 'md'; // sm, md, lg
  
  function handleClose() {
    if (loading) return; // Prevent closing while loading
    dispatch('close');
  }
  
  function handleConfirm() {
    dispatch('confirm');
  }
  
  function handleCancel() {
    if (loading) return; // Prevent canceling while loading
    dispatch('cancel');
    handleClose();
  }
  
  function handleKeydown(event) {
    if (event.key === 'Escape' && !loading) {
      handleClose();
    }
  }
  
  function handleBackdropClick(event) {
    if (event.target === event.currentTarget && !loading) {
      handleClose();
    }
  }
  
  $: sizeClasses = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl'
  };
</script>

{#if open}
  <!-- Backdrop -->
  <div 
    class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
    on:click={handleBackdropClick}
    on:keydown={handleKeydown}
    role="dialog"
    aria-modal="true"
    aria-labelledby="modal-title"
  >
    <!-- Modal -->
    <div 
      class="bg-white rounded-2xl shadow-2xl w-full {sizeClasses[size]} transform transition-all duration-200 scale-100"
      class:opacity-50={loading}
      class:pointer-events-none={loading}
    >
      <!-- Header -->
      {#if title}
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 id="modal-title" class="text-lg font-semibold text-gray-900">
            {title}
          </h3>
        </div>
      {/if}
      
      <!-- Content -->
      <div class="px-6 py-4">
        <slot />
      </div>
      
      <!-- Footer -->
      <div class="px-6 py-4 border-t border-gray-200 flex justify-end space-x-3">
        <Button
          variant="outline"
          on:click={handleCancel}
          disabled={loading}
        >
          {cancelText}
        </Button>
        <Button
          variant={confirmVariant}
          on:click={handleConfirm}
          {loading}
        >
          {confirmText}
        </Button>
      </div>
    </div>
  </div>
{/if}

<style>
  /* Ensure modal appears above everything else */
  :global(body:has(.modal-open)) {
    overflow: hidden;
  }
</style>