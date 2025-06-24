<script>
  import { createEventDispatcher } from 'svelte';
  
  const dispatch = createEventDispatcher();
  
  export let recipeData = {};
  export let extractionData = {};
  export let editable = true;
  
  let editedData = { ...recipeData };
  let showConfidenceDetails = false;
  let showAiSuggestions = {};
  let hasUnsavedChanges = false;
  
  // Watch for changes
  $: {
    const hasChanges = JSON.stringify(editedData) !== JSON.stringify(recipeData);
    if (hasChanges !== hasUnsavedChanges) {
      hasUnsavedChanges = hasChanges;
      dispatch('changeStatus', { hasUnsavedChanges });
    }
  }
  
  function getFieldConfidence(fieldName) {
    return extractionData?.field_confidence?.[fieldName]?.score || 0.5;
  }
  
  function getConfidenceColor(confidence) {
    if (confidence >= 0.8) return '#22c55e'; // green
    if (confidence >= 0.6) return '#f59e0b'; // yellow
    if (confidence >= 0.4) return '#ef4444'; // red
    return '#94a3b8'; // gray
  }
  
  function getConfidenceText(confidence) {
    if (confidence >= 0.8) return 'High Confidence';
    if (confidence >= 0.6) return 'Medium Confidence';
    if (confidence >= 0.4) return 'Low Confidence';
    return 'Very Low Confidence';
  }
  
  function getDataSources(fieldName) {
    const sources = extractionData?.field_confidence?.[fieldName]?.data_sources || ['text'];
    return sources.map(source => {
      switch (source) {
        case 'text': return '📄 Text';
        case 'visual': return '🎥 Video';
        case 'audio': return '🎤 Audio';
        default: return source;
      }
    }).join(', ');
  }
  
  function toggleAiSuggestions(fieldName) {
    showAiSuggestions[fieldName] = !showAiSuggestions[fieldName];
    showAiSuggestions = { ...showAiSuggestions };
  }
  
  function acceptAiSuggestion(fieldName, suggestion) {
    editedData[fieldName] = suggestion;
    editedData = { ...editedData };
    showAiSuggestions[fieldName] = false;
    showAiSuggestions = { ...showAiSuggestions };
  }
  
  function addIngredient() {
    if (!editedData.ingredients) editedData.ingredients = [];
    editedData.ingredients = [...editedData.ingredients, ''];
    editedData = { ...editedData };
  }
  
  function removeIngredient(index) {
    editedData.ingredients = editedData.ingredients.filter((_, i) => i !== index);
    editedData = { ...editedData };
  }
  
  function addInstructionStep() {
    if (!editedData.instructions) editedData.instructions = '';
    const currentSteps = editedData.instructions.split('\n').filter(step => step.trim());
    const newStepNumber = currentSteps.length + 1;
    editedData.instructions = [...currentSteps, `${newStepNumber}. `].join('\n');
    editedData = { ...editedData };
  }
  
  function saveChanges() {
    dispatch('save', { editedData });
  }
  
  function resetChanges() {
    editedData = { ...recipeData };
    hasUnsavedChanges = false;
  }
  
  // Mock AI suggestions (in real app, these would come from the backend)
  const mockSuggestions = {
    title: [
      'Delicious Homemade Pasta Recipe',
      'Quick & Easy Pasta Dish',
      'Traditional Italian Pasta'
    ],
    ingredients: [
      'pasta',
      'olive oil', 
      'garlic',
      'parmesan cheese',
      'fresh basil'
    ],
    category: [
      'Main Course',
      'Italian',
      'Dinner'
    ]
  };
</script>

<div class="smart-recipe-editor">
  <div class="editor-header">
    <h3>Smart Recipe Editor</h3>
    <div class="confidence-toggle">
      <label>
        <input 
          type="checkbox" 
          bind:checked={showConfidenceDetails}
        />
        Show Confidence Details
      </label>
    </div>
  </div>
  
  {#if hasUnsavedChanges}
    <div class="unsaved-changes-banner">
      <span>You have unsaved changes</span>
      <div class="banner-actions">
        <button class="btn-secondary" on:click={resetChanges}>Reset</button>
        <button class="btn-primary" on:click={saveChanges}>Save Changes</button>
      </div>
    </div>
  {/if}
  
  <!-- Recipe Title -->
  <div class="field-section">
    <div class="field-header">
      <label for="title">Recipe Title</label>
      {#if showConfidenceDetails}
        <div class="confidence-indicator">
          <div 
            class="confidence-dot" 
            style="background-color: {getConfidenceColor(getFieldConfidence('title'))}"
            title="{getConfidenceText(getFieldConfidence('title'))}"
          ></div>
          <span class="confidence-text">{(getFieldConfidence('title') * 100).toFixed(0)}%</span>
          <span class="data-sources">{getDataSources('title')}</span>
        </div>
      {/if}
      <button 
        class="ai-suggestions-btn"
        on:click={() => toggleAiSuggestions('title')}
      >
        💡 AI Suggestions
      </button>
    </div>
    
    <input 
      id="title"
      type="text" 
      bind:value={editedData.title}
      disabled={!editable}
      class="field-input"
      placeholder="Enter recipe title..."
    />
    
    {#if showAiSuggestions.title}
      <div class="ai-suggestions">
        <div class="suggestions-header">AI Suggestions:</div>
        {#each mockSuggestions.title as suggestion}
          <div class="suggestion-item">
            <span class="suggestion-text">{suggestion}</span>
            <button 
              class="suggestion-accept"
              on:click={() => acceptAiSuggestion('title', suggestion)}
            >
              Use This
            </button>
          </div>
        {/each}
      </div>
    {/if}
  </div>
  
  <!-- Category -->
  <div class="field-section">
    <div class="field-header">
      <label for="category">Category</label>
      {#if showConfidenceDetails}
        <div class="confidence-indicator">
          <div 
            class="confidence-dot" 
            style="background-color: {getConfidenceColor(getFieldConfidence('category'))}"
          ></div>
          <span class="confidence-text">{(getFieldConfidence('category') * 100).toFixed(0)}%</span>
          <span class="data-sources">{getDataSources('category')}</span>
        </div>
      {/if}
    </div>
    
    <select 
      id="category" 
      bind:value={editedData.category}
      disabled={!editable}
      class="field-input"
    >
      <option value="">Select category...</option>
      <option value="Main Course">Main Course</option>
      <option value="Desserts">Desserts</option>
      <option value="Starters">Starters</option>
      <option value="Beverages">Beverages</option>
      <option value="Snacks">Snacks</option>
      <option value="Breakfast">Breakfast</option>
      <option value="Salads">Salads</option>
    </select>
  </div>
  
  <!-- Cooking Time & Difficulty -->
  <div class="field-row">
    <div class="field-section">
      <div class="field-header">
        <label for="cookingTime">Cooking Time (minutes)</label>
        {#if showConfidenceDetails}
          <div class="confidence-indicator">
            <div 
              class="confidence-dot" 
              style="background-color: {getConfidenceColor(getFieldConfidence('cookingTime'))}"
            ></div>
            <span class="confidence-text">{(getFieldConfidence('cookingTime') * 100).toFixed(0)}%</span>
          </div>
        {/if}
      </div>
      <input 
        id="cookingTime"
        type="number" 
        min="1" 
        max="600"
        bind:value={editedData.cookingTime}
        disabled={!editable}
        class="field-input"
      />
    </div>
    
    <div class="field-section">
      <div class="field-header">
        <label for="difficulty">Difficulty</label>
        {#if showConfidenceDetails}
          <div class="confidence-indicator">
            <div 
              class="confidence-dot" 
              style="background-color: {getConfidenceColor(getFieldConfidence('difficulty'))}"
            ></div>
            <span class="confidence-text">{(getFieldConfidence('difficulty') * 100).toFixed(0)}%</span>
          </div>
        {/if}
      </div>
      <select 
        id="difficulty" 
        bind:value={editedData.difficulty}
        disabled={!editable}
        class="field-input"
      >
        <option value="">Select difficulty...</option>
        <option value="Easy">Easy</option>
        <option value="Medium">Medium</option>
        <option value="Hard">Hard</option>
      </select>
    </div>
  </div>
  
  <!-- Ingredients -->
  <div class="field-section">
    <div class="field-header">
      <label>Ingredients</label>
      {#if showConfidenceDetails}
        <div class="confidence-indicator">
          <div 
            class="confidence-dot" 
            style="background-color: {getConfidenceColor(getFieldConfidence('ingredients'))}"
          ></div>
          <span class="confidence-text">{(getFieldConfidence('ingredients') * 100).toFixed(0)}%</span>
          <span class="data-sources">{getDataSources('ingredients')}</span>
        </div>
      {/if}
      <button 
        class="ai-suggestions-btn"
        on:click={() => toggleAiSuggestions('ingredients')}
      >
        💡 AI Suggestions
      </button>
    </div>
    
    <div class="ingredients-list">
      {#if editedData.ingredients && editedData.ingredients.length > 0}
        {#each editedData.ingredients as ingredient, index}
          <div class="ingredient-item">
            <input 
              type="text" 
              bind:value={editedData.ingredients[index]}
              disabled={!editable}
              class="ingredient-input"
              placeholder="Enter ingredient..."
            />
            {#if editable}
              <button 
                class="remove-ingredient"
                on:click={() => removeIngredient(index)}
              >
                ✗
              </button>
            {/if}
          </div>
        {/each}
      {:else}
        <div class="no-ingredients">No ingredients added yet</div>
      {/if}
      
      {#if editable}
        <button class="add-ingredient" on:click={addIngredient}>
          + Add Ingredient
        </button>
      {/if}
    </div>
    
    {#if showAiSuggestions.ingredients}
      <div class="ai-suggestions">
        <div class="suggestions-header">Suggested Ingredients:</div>
        <div class="ingredient-suggestions">
          {#each mockSuggestions.ingredients as suggestion}
            <button 
              class="ingredient-suggestion"
              on:click={() => {
                if (!editedData.ingredients) editedData.ingredients = [];
                if (!editedData.ingredients.includes(suggestion)) {
                  editedData.ingredients = [...editedData.ingredients, suggestion];
                }
              }}
            >
              + {suggestion}
            </button>
          {/each}
        </div>
      </div>
    {/if}
  </div>
  
  <!-- Instructions -->
  <div class="field-section">
    <div class="field-header">
      <label for="instructions">Cooking Instructions</label>
      {#if showConfidenceDetails}
        <div class="confidence-indicator">
          <div 
            class="confidence-dot" 
            style="background-color: {getConfidenceColor(getFieldConfidence('instructions'))}"
          ></div>
          <span class="confidence-text">{(getFieldConfidence('instructions') * 100).toFixed(0)}%</span>
          <span class="data-sources">{getDataSources('instructions')}</span>
        </div>
      {/if}
      {#if editable}
        <button class="add-step-btn" on:click={addInstructionStep}>
          + Add Step
        </button>
      {/if}
    </div>
    
    <textarea 
      id="instructions"
      bind:value={editedData.instructions}
      disabled={!editable}
      class="field-textarea"
      rows="8"
      placeholder="Enter step-by-step cooking instructions..."
    ></textarea>
  </div>
  
  <!-- Dietary Information -->
  <div class="field-section">
    <div class="field-header">
      <label>Dietary Information</label>
      {#if showConfidenceDetails}
        <div class="confidence-indicator">
          <div 
            class="confidence-dot" 
            style="background-color: {getConfidenceColor(getFieldConfidence('dietaryInfo'))}"
          ></div>
          <span class="confidence-text">{(getFieldConfidence('dietaryInfo') * 100).toFixed(0)}%</span>
        </div>
      {/if}
    </div>
    
    <div class="dietary-tags">
      {#if editedData.dietaryInfo && editedData.dietaryInfo.length > 0}
        {#each editedData.dietaryInfo as diet}
          <span class="dietary-tag">{diet}</span>
        {/each}
      {:else}
        <span class="no-dietary-info">No dietary restrictions detected</span>
      {/if}
    </div>
  </div>
  
  <!-- Tags -->
  <div class="field-section">
    <div class="field-header">
      <label>Tags</label>
      {#if showConfidenceDetails}
        <div class="confidence-indicator">
          <div 
            class="confidence-dot" 
            style="background-color: {getConfidenceColor(getFieldConfidence('tags'))}"
          ></div>
          <span class="confidence-text">{(getFieldConfidence('tags') * 100).toFixed(0)}%</span>
        </div>
      {/if}
    </div>
    
    <div class="recipe-tags">
      {#if editedData.tags && editedData.tags.length > 0}
        {#each editedData.tags as tag}
          <span class="recipe-tag">#{tag}</span>
        {/each}
      {:else}
        <span class="no-tags">No tags generated</span>
      {/if}
    </div>
  </div>
  
  <!-- Overall Confidence Summary -->
  {#if showConfidenceDetails && extractionData.overall_confidence}
    <div class="confidence-summary">
      <h4>Extraction Summary</h4>
      <div class="summary-item">
        <strong>Overall Confidence:</strong> 
        <span class="confidence-score" style="color: {getConfidenceColor(extractionData.overall_confidence)}">
          {(extractionData.overall_confidence * 100).toFixed(0)}%
        </span>
      </div>
      {#if extractionData.data_sources}
        <div class="summary-item">
          <strong>Data Sources:</strong> {extractionData.data_sources.join(', ')}
        </div>
      {/if}
      {#if extractionData.recommendations && extractionData.recommendations.length > 0}
        <div class="recommendations">
          <strong>Recommendations:</strong>
          <ul>
            {#each extractionData.recommendations as recommendation}
              <li>{recommendation}</li>
            {/each}
          </ul>
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  .smart-recipe-editor {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  }
  
  .editor-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    padding-bottom: 16px;
    border-bottom: 1px solid #e2e8f0;
  }
  
  .editor-header h3 {
    margin: 0;
    color: #2d3748;
    font-size: 24px;
    font-weight: 600;
  }
  
  .confidence-toggle label {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    color: #64748b;
    cursor: pointer;
  }
  
  .unsaved-changes-banner {
    background: #fef3c7;
    border: 1px solid #f59e0b;
    border-radius: 8px;
    padding: 12px 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    color: #92400e;
    font-weight: 500;
  }
  
  .banner-actions {
    display: flex;
    gap: 8px;
  }
  
  .banner-actions button {
    padding: 6px 12px;
    border: none;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
  }
  
  .btn-primary {
    background: #0ea5e9;
    color: white;
  }
  
  .btn-secondary {
    background: transparent;
    color: #92400e;
    border: 1px solid #92400e;
  }
  
  .field-section {
    margin-bottom: 24px;
  }
  
  .field-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
  }
  
  .field-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 8px;
  }
  
  .field-header label {
    font-weight: 600;
    color: #374151;
    font-size: 14px;
  }
  
  .confidence-indicator {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
  }
  
  .confidence-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
  }
  
  .confidence-text {
    font-weight: 600;
    color: #374151;
  }
  
  .data-sources {
    color: #64748b;
    font-style: italic;
  }
  
  .ai-suggestions-btn {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 12px;
    cursor: pointer;
    color: #64748b;
    margin-left: auto;
  }
  
  .ai-suggestions-btn:hover {
    background: #e2e8f0;
  }
  
  .field-input, .field-textarea {
    width: 100%;
    padding: 12px;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    font-size: 14px;
    font-family: inherit;
    background: white;
  }
  
  .field-input:focus, .field-textarea:focus {
    outline: none;
    border-color: #0ea5e9;
    box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1);
  }
  
  .field-input:disabled, .field-textarea:disabled {
    background: #f8fafc;
    color: #64748b;
  }
  
  .ai-suggestions {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: 8px;
    padding: 12px;
    margin-top: 8px;
  }
  
  .suggestions-header {
    font-size: 12px;
    font-weight: 600;
    color: #166534;
    margin-bottom: 8px;
  }
  
  .suggestion-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 0;
    border-bottom: 1px solid #dcfce7;
  }
  
  .suggestion-item:last-child {
    border-bottom: none;
  }
  
  .suggestion-text {
    color: #374151;
    font-size: 14px;
  }
  
  .suggestion-accept {
    background: #22c55e;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 12px;
    cursor: pointer;
  }
  
  .ingredients-list {
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 12px;
    background: white;
  }
  
  .ingredient-item {
    display: flex;
    gap: 8px;
    margin-bottom: 8px;
  }
  
  .ingredient-item:last-child {
    margin-bottom: 0;
  }
  
  .ingredient-input {
    flex: 1;
    padding: 8px;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    font-size: 14px;
  }
  
  .remove-ingredient {
    background: #ef4444;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 4px 8px;
    cursor: pointer;
    font-size: 12px;
  }
  
  .add-ingredient {
    background: #0ea5e9;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 14px;
    cursor: pointer;
    margin-top: 8px;
  }
  
  .no-ingredients {
    color: #94a3b8;
    font-style: italic;
    text-align: center;
    padding: 20px;
  }
  
  .ingredient-suggestions {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }
  
  .ingredient-suggestion {
    background: white;
    border: 1px solid #22c55e;
    color: #22c55e;
    border-radius: 16px;
    padding: 4px 12px;
    font-size: 12px;
    cursor: pointer;
  }
  
  .ingredient-suggestion:hover {
    background: #22c55e;
    color: white;
  }
  
  .add-step-btn {
    background: #0ea5e9;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 6px 12px;
    font-size: 12px;
    cursor: pointer;
    margin-left: auto;
  }
  
  .dietary-tags, .recipe-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .dietary-tag, .recipe-tag {
    background: #e0e7ff;
    color: #3730a3;
    padding: 4px 12px;
    border-radius: 16px;
    font-size: 12px;
    font-weight: 500;
  }
  
  .recipe-tag {
    background: #fef3c7;
    color: #92400e;
  }
  
  .no-dietary-info, .no-tags {
    color: #94a3b8;
    font-style: italic;
  }
  
  .confidence-summary {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 20px;
    margin-top: 24px;
  }
  
  .confidence-summary h4 {
    margin: 0 0 16px 0;
    color: #374151;
    font-size: 16px;
  }
  
  .summary-item {
    margin-bottom: 8px;
    font-size: 14px;
    color: #374151;
  }
  
  .confidence-score {
    font-weight: 600;
  }
  
  .recommendations {
    margin-top: 12px;
  }
  
  .recommendations ul {
    margin: 4px 0 0 0;
    padding-left: 20px;
  }
  
  .recommendations li {
    font-size: 13px;
    color: #64748b;
    margin-bottom: 4px;
  }
  
  @media (max-width: 640px) {
    .smart-recipe-editor {
      padding: 16px;
    }
    
    .editor-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 12px;
    }
    
    .field-row {
      grid-template-columns: 1fr;
    }
    
    .field-header {
      flex-wrap: wrap;
    }
    
    .unsaved-changes-banner {
      flex-direction: column;
      gap: 12px;
      text-align: center;
    }
  }
</style>