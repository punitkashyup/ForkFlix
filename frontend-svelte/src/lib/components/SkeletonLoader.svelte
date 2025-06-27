<script>
  export let type = 'card'; // card, list, text, button
  export let count = 1;
  export let height = 'auto';
  export let width = 'auto';
</script>

<div class="skeleton-container">
  {#each Array(count) as _, i}
    <div class="skeleton skeleton-{type}" style="height: {height}; width: {width}">
      {#if type === 'card'}
        <div class="skeleton-image"></div>
        <div class="skeleton-content">
          <div class="skeleton-title"></div>
          <div class="skeleton-text"></div>
          <div class="skeleton-text short"></div>
        </div>
      {:else if type === 'list'}
        <div class="skeleton-list-item">
          <div class="skeleton-avatar"></div>
          <div class="skeleton-list-content">
            <div class="skeleton-title"></div>
            <div class="skeleton-text"></div>
          </div>
        </div>
      {:else if type === 'text'}
        <div class="skeleton-line"></div>
      {:else if type === 'button'}
        <div class="skeleton-button"></div>
      {/if}
    </div>
  {/each}
</div>

<style>
  .skeleton-container {
    display: contents;
  }

  .skeleton {
    background-color: #f3f4f6;
    border-radius: 8px;
    overflow: hidden;
    position: relative;
  }

  .skeleton::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(
      90deg,
      transparent,
      rgba(255, 255, 255, 0.6),
      transparent
    );
    animation: shimmer 1.5s infinite;
  }

  @keyframes shimmer {
    0% {
      left: -100%;
    }
    100% {
      left: 100%;
    }
  }

  /* Card skeleton */
  .skeleton-card {
    padding: 0;
    height: 300px;
    margin-bottom: 1rem;
  }

  .skeleton-image {
    height: 160px;
    background-color: #e5e7eb;
    margin-bottom: 12px;
  }

  .skeleton-content {
    padding: 16px;
  }

  .skeleton-title {
    height: 20px;
    background-color: #e5e7eb;
    border-radius: 4px;
    margin-bottom: 8px;
    width: 80%;
  }

  .skeleton-text {
    height: 14px;
    background-color: #e5e7eb;
    border-radius: 4px;
    margin-bottom: 6px;
    width: 100%;
  }

  .skeleton-text.short {
    width: 60%;
  }

  /* List skeleton */
  .skeleton-list {
    padding: 12px;
    margin-bottom: 8px;
  }

  .skeleton-list-item {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .skeleton-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background-color: #e5e7eb;
    flex-shrink: 0;
  }

  .skeleton-list-content {
    flex: 1;
  }

  /* Text skeleton */
  .skeleton-line {
    height: 16px;
    background-color: #e5e7eb;
    border-radius: 4px;
    margin-bottom: 8px;
  }

  /* Button skeleton */
  .skeleton-button {
    height: 40px;
    background-color: #e5e7eb;
    border-radius: 8px;
    width: 120px;
  }
</style>