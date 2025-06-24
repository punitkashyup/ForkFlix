<script>
  import { onDestroy } from 'svelte';
  import { createEventDispatcher } from 'svelte';
  import { apiService } from '$lib/services/api.js';
  
  const dispatch = createEventDispatcher();
  
  export let instagramUrl = '';
  export let enableVisualAnalysis = true;
  export let enableAudioTranscription = true;
  export let maxProcessingTime = 30;
  
  let extractionPhases = [
    {
      phase: 1,
      name: 'Text Analysis',
      icon: '📄',
      message: 'Reading caption and description...',
      progress: 0,
      status: 'waiting',
      data: null,
      confidence: 0,
      estimatedTime: '1-2 seconds'
    },
    {
      phase: 2,
      name: 'Video Analysis',
      icon: '🎥',
      message: 'Analyzing video frames for ingredients...',
      progress: 0,
      status: 'waiting',
      data: null,
      confidence: 0,
      estimatedTime: '10-15 seconds'
    },
    {
      phase: 3,
      name: 'Audio Processing',
      icon: '🎤',
      message: 'Transcribing cooking instructions...',
      progress: 0,
      status: 'waiting',
      data: null,
      confidence: 0,
      estimatedTime: '5-10 seconds'
    },
    {
      phase: 4,
      name: 'AI-Powered Fusion',
      icon: '🤖',
      message: 'AI analyzing all sources for optimal recipe extraction...',
      progress: 0,
      status: 'waiting',
      data: null,
      confidence: 0,
      estimatedTime: '2-3 seconds'
    },
    {
      phase: 5,
      name: 'Mistral AI Final Processing',
      icon: '🧠',
      message: 'Mistral AI extracting structured recipe data for maximum accuracy...',
      progress: 0,
      status: 'waiting',
      data: null,
      confidence: 0,
      estimatedTime: '5-10 seconds'
    }
  ];
  
  let isExtracting = false;
  let overallProgress = 0;
  let currentPhase = 0;
  let finalResult = null;
  let error = null;
  let eventSource = null;
  let startTime = null;
  
  async function startExtraction() {
    if (!instagramUrl) {
      error = 'Please provide an Instagram URL';
      return;
    }
    
    // Test API connection first
    try {
      console.log('🔍 Testing multi-modal API connection...');
      await apiService.testConnection();
      console.log('✅ API connection successful, starting extraction...');
    } catch (connectionError) {
      console.error('❌ API connection test failed:', connectionError);
      error = `API connection failed: ${connectionError.message}. Make sure the backend server is running on http://localhost:8000`;
      return;
    }
    
    isExtracting = true;
    error = null;
    finalResult = null;
    currentPhase = 1;
    startTime = Date.now();
    
    // Reset all phases
    extractionPhases = extractionPhases.map(phase => ({
      ...phase,
      status: 'waiting',
      progress: 0,
      data: null,
      confidence: 0
    }));
    
    try {
      // Start streaming extraction using API service
      const response = await apiService.startMultiModalExtraction({
        instagram_url: instagramUrl,
        enable_visual_analysis: enableVisualAnalysis,
        enable_audio_transcription: enableAudioTranscription,
        max_processing_time: maxProcessingTime
      });
      
      // Set up Server-Sent Events
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              handleExtractionUpdate(data);
            } catch (e) {
              console.error('Error parsing SSE data:', e);
            }
          }
        }
      }
      
    } catch (err) {
      error = err.message;
      isExtracting = false;
      dispatch('error', { error: err.message });
    }
  }
  
  function handleExtractionUpdate(data) {
    if (data.event === 'extraction_error') {
      error = data.error;
      isExtracting = false;
      dispatch('error', { error: data.error });
      return;
    }
    
    if (data.event === 'extraction_completed') {
      isExtracting = false;
      const totalTime = (Date.now() - startTime) / 1000;
      dispatch('completed', { 
        result: finalResult, 
        totalTime: totalTime.toFixed(1) 
      });
      return;
    }
    
    const phaseIndex = data.phase - 1;
    if (phaseIndex >= 0 && phaseIndex < extractionPhases.length) {
      // Update specific phase
      extractionPhases[phaseIndex] = {
        ...extractionPhases[phaseIndex],
        status: data.status,
        progress: data.progress || 0,
        confidence: data.confidence || 0
      };
      
      if (data.status === 'processing') {
        extractionPhases[phaseIndex].message = data.message;
        currentPhase = data.phase;
      } else if (data.status === 'completed') {
        extractionPhases[phaseIndex].data = data.data;
        // Capture Phase 5 (Mistral AI) as the final result for maximum accuracy
        if (data.phase === 5) {
          finalResult = data.data;
        }
        // Fallback to Phase 4 if Phase 5 is not available
        else if (data.phase === 4 && !finalResult) {
          finalResult = data.data;
        }
      }
      
      // Update overall progress
      overallProgress = data.progress || 0;
      
      // Trigger reactivity
      extractionPhases = [...extractionPhases];
      
      // Dispatch phase update
      dispatch('phaseUpdate', {
        phase: data.phase,
        status: data.status,
        data: data.data,
        confidence: data.confidence
      });
    }
  }
  
  function cancelExtraction() {
    if (eventSource) {
      eventSource.close();
      eventSource = null;
    }
    isExtracting = false;
    currentPhase = 0;
    dispatch('cancelled');
  }
  
  function getPhaseStatusClass(phase) {
    switch (phase.status) {
      case 'completed': return 'phase-completed';
      case 'processing': return 'phase-processing';
      case 'failed': return 'phase-failed';
      default: return 'phase-waiting';
    }
  }
  
  function getConfidenceClass(confidence) {
    if (confidence >= 0.8) return 'confidence-high';
    if (confidence >= 0.6) return 'confidence-medium';
    if (confidence >= 0.4) return 'confidence-low';
    return 'confidence-very-low';
  }
  
  onDestroy(() => {
    if (eventSource) {
      eventSource.close();
    }
  });
</script>

<div class="multimodal-extraction">
  <div class="extraction-header">
    <h3>Multi-Modal Recipe Extraction</h3>
    <p class="extraction-description">
      Advanced AI system that analyzes text, video, and audio to extract accurate recipe information
    </p>
  </div>
  
  <!-- Overall Progress -->
  {#if isExtracting}
    <div class="overall-progress">
      <div class="progress-header">
        <span class="progress-label">Overall Progress</span>
        <span class="progress-percentage">{overallProgress}%</span>
      </div>
      <div class="progress-bar">
        <div 
          class="progress-fill" 
          style="width: {overallProgress}%"
        ></div>
      </div>
      <div class="current-phase">
        Currently: Phase {currentPhase} - {extractionPhases[currentPhase - 1]?.name}
      </div>
    </div>
  {/if}
  
  <!-- Extraction Phases -->
  <div class="extraction-phases">
    {#each extractionPhases as phase, index}
      <div class="phase-card {getPhaseStatusClass(phase)}">
        <div class="phase-header">
          <div class="phase-icon">{phase.icon}</div>
          <div class="phase-info">
            <h4 class="phase-name">{phase.name}</h4>
            <p class="phase-message">{phase.message}</p>
            <span class="phase-time">{phase.estimatedTime}</span>
          </div>
          <div class="phase-status">
            {#if phase.status === 'completed'}
              <div class="status-icon completed">✓</div>
              <div class="confidence-score {getConfidenceClass(phase.confidence)}">
                {(phase.confidence * 100).toFixed(0)}%
              </div>
            {:else if phase.status === 'processing'}
              <div class="status-icon processing">⟳</div>
              <div class="phase-progress">{phase.progress}%</div>
            {:else if phase.status === 'failed'}
              <div class="status-icon failed">✗</div>
            {:else}
              <div class="status-icon waiting">○</div>
            {/if}
          </div>
        </div>
        
        {#if phase.status === 'processing'}
          <div class="phase-progress-bar">
            <div 
              class="phase-progress-fill" 
              style="width: {phase.progress}%"
            ></div>
          </div>
        {/if}
        
        {#if phase.data && phase.status === 'completed'}
          <div class="phase-results">
            <div class="results-summary">
              {#if phase.data.recipe_data}
                <!-- Phase 5: Mistral AI structured data -->
                <div class="result-item">
                  <strong>Recipe:</strong> {phase.data.recipe_data.recipe_name}
                </div>
                <div class="result-item">
                  <strong>Ingredients:</strong> {phase.data.recipe_data.ingredients?.length || 0} items
                </div>
                <div class="result-item">
                  <strong>Category:</strong> {phase.data.recipe_data.category}
                </div>
                {#if phase.data.recipe_data.cooking_time?.total_minutes}
                  <div class="result-item">
                    <strong>Total Time:</strong> {phase.data.recipe_data.cooking_time.total_minutes} min
                  </div>
                {/if}
              {:else}
                <!-- Other phases: traditional data -->
                {#if phase.data.ingredients}
                  <div class="result-item">
                    <strong>Ingredients:</strong> {Array.isArray(phase.data.ingredients) ? phase.data.ingredients.slice(0, 3).join(', ') : phase.data.ingredients}
                    {#if Array.isArray(phase.data.ingredients) && phase.data.ingredients.length > 3}+ {phase.data.ingredients.length - 3} more{/if}
                  </div>
                {/if}
                {#if phase.data.category}
                  <div class="result-item">
                    <strong>Category:</strong> {phase.data.category}
                  </div>
                {/if}
                {#if phase.data.cookingTime}
                  <div class="result-item">
                    <strong>Cooking Time:</strong> {phase.data.cookingTime} minutes
                  </div>
                {/if}
              {/if}
            </div>
          </div>
        {/if}
      </div>
    {/each}
  </div>
  
  <!-- Control Buttons -->
  <div class="extraction-controls">
    {#if !isExtracting}
      <button 
        class="btn-primary extract-btn" 
        on:click={startExtraction}
        disabled={!instagramUrl}
      >
        Start Multi-Modal Extraction
      </button>
    {:else}
      <button 
        class="btn-secondary cancel-btn" 
        on:click={cancelExtraction}
      >
        Cancel Extraction
      </button>
    {/if}
  </div>
  
  <!-- Options -->
  <div class="extraction-options">
    <label class="option-checkbox">
      <input 
        type="checkbox" 
        bind:checked={enableVisualAnalysis}
        disabled={isExtracting}
      />
      <span class="checkmark"></span>
      Enable Video Frame Analysis
    </label>
    
    <label class="option-checkbox">
      <input 
        type="checkbox" 
        bind:checked={enableAudioTranscription}
        disabled={isExtracting}
      />
      <span class="checkmark"></span>
      Enable Audio Transcription
    </label>
  </div>
  
  <!-- Error Display -->
  {#if error}
    <div class="error-message">
      <div class="error-icon">⚠️</div>
      <div class="error-text">{error}</div>
    </div>
  {/if}
  
  <!-- Final Results Preview -->
  {#if finalResult && !isExtracting}
    <div class="final-results">
      {#if finalResult.recipe_data}
        <!-- Phase 5: Mistral AI Results -->
        <h4>🧠 Mistral AI Extraction Complete!</h4>
        <div class="final-confidence">
          Mistral AI Confidence: 
          <span class="confidence-score {getConfidenceClass(finalResult.confidence)}">
            {(finalResult.confidence * 100).toFixed(0)}%
          </span>
        </div>
        <div class="final-summary">
          <div><strong>Recipe Name:</strong> {finalResult.recipe_data.recipe_name}</div>
          <div><strong>Category:</strong> {finalResult.recipe_data.category}</div>
          <div><strong>Ingredients:</strong> {finalResult.recipe_data.ingredients?.length || 0} items</div>
          <div><strong>Instructions:</strong> {finalResult.recipe_data.instructions?.length || 0} steps</div>
          {#if finalResult.recipe_data.cooking_time?.total_minutes}
            <div><strong>Total Time:</strong> {finalResult.recipe_data.cooking_time.total_minutes} minutes</div>
          {/if}
          <div><strong>Processing Method:</strong> 5-Phase Multimodal + Mistral AI</div>
        </div>
      {:else}
        <!-- Phase 4: AI Fusion Results (Fallback) -->
        <h4>🤖 AI-Powered Extraction Complete!</h4>
        <div class="final-confidence">
          AI Fusion Confidence: 
          <span class="confidence-score {getConfidenceClass(finalResult.confidence)}">
            {(finalResult.confidence * 100).toFixed(0)}%
          </span>
        </div>
        <div class="final-summary">
          <div><strong>Fusion Method:</strong> {finalResult.fusionMethod || 'AI-Weighted Analysis'}</div>
          <div><strong>Sources Used:</strong> {finalResult.dataSources?.join(', ') || 'Text'}</div>
          <div><strong>Fields Extracted:</strong> {finalResult.extractedFields?.length || 0} fields</div>
          {#if finalResult.sourceWeights}
            <div class="source-weights">
              <strong>Source Weights:</strong>
              {#if finalResult.sourceWeights.text}
                Text: {(finalResult.sourceWeights.text * 100).toFixed(0)}%
              {/if}
              {#if finalResult.sourceWeights.audio}
                Audio: {(finalResult.sourceWeights.audio * 100).toFixed(0)}%
              {/if}
              {#if finalResult.sourceWeights.visual}
                Video: {(finalResult.sourceWeights.visual * 100).toFixed(0)}%
              {/if}
            </div>
          {/if}
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  .multimodal-extraction {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  }
  
  .extraction-header {
    text-align: center;
    margin-bottom: 30px;
  }
  
  .extraction-header h3 {
    color: #2d3748;
    margin-bottom: 8px;
    font-size: 24px;
    font-weight: 600;
  }
  
  .extraction-description {
    color: #64748b;
    font-size: 14px;
    margin: 0;
  }
  
  .overall-progress {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 24px;
  }
  
  .progress-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }
  
  .progress-label {
    font-weight: 600;
    color: #374151;
  }
  
  .progress-percentage {
    font-weight: 700;
    color: #0ea5e9;
    font-size: 18px;
  }
  
  .progress-bar {
    width: 100%;
    height: 8px;
    background: #e2e8f0;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 8px;
  }
  
  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #0ea5e9, #3b82f6);
    border-radius: 4px;
    transition: width 0.3s ease;
  }
  
  .current-phase {
    font-size: 12px;
    color: #64748b;
    font-style: italic;
  }
  
  .extraction-phases {
    display: flex;
    flex-direction: column;
    gap: 16px;
    margin-bottom: 24px;
  }
  
  .phase-card {
    border: 2px solid #e2e8f0;
    border-radius: 12px;
    padding: 20px;
    transition: all 0.3s ease;
  }
  
  .phase-card.phase-waiting {
    background: #f8fafc;
    border-color: #e2e8f0;
  }
  
  .phase-card.phase-processing {
    background: #fef3c7;
    border-color: #f59e0b;
    box-shadow: 0 4px 12px rgba(245, 158, 11, 0.2);
  }
  
  .phase-card.phase-completed {
    background: #dcfce7;
    border-color: #22c55e;
    box-shadow: 0 4px 12px rgba(34, 197, 94, 0.2);
  }
  
  .phase-card.phase-failed {
    background: #fee2e2;
    border-color: #ef4444;
  }
  
  .phase-header {
    display: flex;
    align-items: center;
    gap: 16px;
  }
  
  .phase-icon {
    font-size: 24px;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: white;
    border-radius: 50%;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
  
  .phase-info {
    flex: 1;
  }
  
  .phase-name {
    margin: 0 0 4px 0;
    font-size: 16px;
    font-weight: 600;
    color: #374151;
  }
  
  .phase-message {
    margin: 0 0 4px 0;
    font-size: 14px;
    color: #64748b;
  }
  
  .phase-time {
    font-size: 12px;
    color: #94a3b8;
    font-style: italic;
  }
  
  .phase-status {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
  }
  
  .status-icon {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 14px;
  }
  
  .status-icon.completed {
    background: #22c55e;
    color: white;
  }
  
  .status-icon.processing {
    background: #f59e0b;
    color: white;
    animation: spin 2s linear infinite;
  }
  
  .status-icon.failed {
    background: #ef4444;
    color: white;
  }
  
  .status-icon.waiting {
    background: #e2e8f0;
    color: #94a3b8;
  }
  
  .confidence-score {
    font-size: 12px;
    font-weight: 600;
    padding: 2px 6px;
    border-radius: 4px;
  }
  
  .confidence-high {
    background: #dcfce7;
    color: #166534;
  }
  
  .confidence-medium {
    background: #fef3c7;
    color: #92400e;
  }
  
  .confidence-low {
    background: #fed7d7;
    color: #c53030;
  }
  
  .confidence-very-low {
    background: #f3f4f6;
    color: #6b7280;
  }
  
  .phase-progress-bar {
    width: 100%;
    height: 4px;
    background: #e2e8f0;
    border-radius: 2px;
    overflow: hidden;
    margin-top: 12px;
  }
  
  .phase-progress-fill {
    height: 100%;
    background: #f59e0b;
    border-radius: 2px;
    transition: width 0.3s ease;
  }
  
  .phase-results {
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid #e2e8f0;
  }
  
  .results-summary {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  
  .result-item {
    font-size: 12px;
    color: #374151;
  }
  
  .extraction-controls {
    display: flex;
    justify-content: center;
    margin-bottom: 20px;
  }
  
  .btn-primary, .btn-secondary {
    padding: 12px 24px;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  
  .btn-primary {
    background: #0ea5e9;
    color: white;
  }
  
  .btn-primary:hover:not(:disabled) {
    background: #0284c7;
    transform: translateY(-1px);
  }
  
  .btn-primary:disabled {
    background: #94a3b8;
    cursor: not-allowed;
  }
  
  .btn-secondary {
    background: #ef4444;
    color: white;
  }
  
  .btn-secondary:hover {
    background: #dc2626;
  }
  
  .extraction-options {
    display: flex;
    gap: 20px;
    justify-content: center;
    margin-bottom: 20px;
  }
  
  .option-checkbox {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    font-size: 14px;
    color: #374151;
  }
  
  .option-checkbox input[type="checkbox"] {
    margin: 0;
  }
  
  .error-message {
    background: #fee2e2;
    border: 1px solid #fecaca;
    border-radius: 8px;
    padding: 16px;
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
  }
  
  .error-icon {
    font-size: 20px;
  }
  
  .error-text {
    color: #dc2626;
    font-weight: 500;
  }
  
  .final-results {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
  }
  
  .final-results h4 {
    color: #166534;
    margin: 0 0 12px 0;
  }
  
  .final-confidence {
    margin-bottom: 12px;
    font-weight: 600;
  }
  
  .final-summary {
    display: flex;
    flex-direction: column;
    gap: 8px;
    font-size: 14px;
    color: #374151;
  }
  
  .source-weights {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    font-size: 12px;
    background: #f8fafc;
    padding: 8px;
    border-radius: 4px;
    margin-top: 4px;
  }
  
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
  
  @media (max-width: 640px) {
    .multimodal-extraction {
      padding: 16px;
    }
    
    .phase-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 12px;
    }
    
    .phase-status {
      align-self: flex-end;
    }
    
    .extraction-options {
      flex-direction: column;
      align-items: center;
    }
    
    .final-summary {
      flex-direction: column;
      gap: 8px;
    }
  }
</style>