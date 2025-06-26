<script>
  import { onDestroy } from 'svelte';
  import { createEventDispatcher } from 'svelte';
  import { apiService } from '$lib/services/api.js';
  import Loading from './Loading.svelte';
  
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
  let timeoutId = null;
  
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
    
    // Set timeout for extraction (5 minutes max)
    timeoutId = setTimeout(() => {
      if (isExtracting) {
        error = 'Extraction timed out. Please try again with a shorter video or check your connection.';
        isExtracting = false;
        dispatch('error', { error: error });
      }
    }, 5 * 60 * 1000);
    
    // Reset all phases
    extractionPhases = extractionPhases.map(phase => ({
      ...phase,
      status: 'waiting',
      progress: 0,
      data: null,
      confidence: 0
    }));
    
    // Add retry logic for streaming
    let retryCount = 0;
    const maxRetries = 3;
    
    while (retryCount <= maxRetries) {
      try {
        console.log(`🚀 Starting extraction attempt ${retryCount + 1}/${maxRetries + 1}`);
        
        // Start streaming extraction using API service
        const response = await apiService.startMultiModalExtraction({
          instagram_url: instagramUrl,
          enable_visual_analysis: enableVisualAnalysis,
          enable_audio_transcription: enableAudioTranscription,
          max_processing_time: maxProcessingTime
        });
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        // Set up Server-Sent Events
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        
        console.log('📡 Streaming connection established, processing data...');
        
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          
          // Keep the last incomplete line in buffer
          buffer = lines.pop() || '';
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const jsonData = line.slice(6);
                if (jsonData.trim()) {
                  const data = JSON.parse(jsonData);
                  handleExtractionUpdate(data);
                }
              } catch (e) {
                console.error('Error parsing SSE data:', e, 'Line:', line);
              }
            }
          }
        }
        
        // If we get here, streaming completed successfully
        console.log('✅ Streaming completed successfully');
        if (timeoutId) {
          clearTimeout(timeoutId);
          timeoutId = null;
        }
        return;
        
      } catch (err) {
        retryCount++;
        console.error(`❌ Extraction attempt ${retryCount} failed:`, err);
        
        if (retryCount > maxRetries) {
          console.log('🔄 Streaming failed, attempting fallback to batch extraction...');
          
          try {
            // Fallback to batch extraction
            const batchResult = await apiService.batchMultiModalExtraction({
              instagram_url: instagramUrl,
              enable_visual_analysis: enableVisualAnalysis,
              enable_audio_transcription: enableAudioTranscription,
              max_processing_time: maxProcessingTime
            });
            
            if (batchResult.success) {
              console.log('✅ Batch extraction completed successfully');
              finalResult = batchResult.data.recipe;
              
              // Simulate completion
              handleExtractionUpdate({
                event: 'extraction_completed',
                phase: 4,
                status: 'completed',
                data: finalResult,
                confidence: finalResult.confidence || 0.8
              });
              
              isExtracting = false;
              const totalTime = (Date.now() - startTime) / 1000;
              dispatch('completed', { 
                result: finalResult, 
                totalTime: totalTime.toFixed(1) 
              });
              return;
            }
          } catch (batchError) {
            console.error('❌ Batch extraction also failed:', batchError);
          }
          
          error = `All extraction methods failed. Please try again later or check your internet connection.`;
          isExtracting = false;
          dispatch('error', { error: error });
          return;
        }
        
        // Wait before retrying (exponential backoff)
        const waitTime = Math.pow(2, retryCount) * 1000;
        console.log(`⏳ Retrying in ${waitTime/1000} seconds...`);
        await new Promise(resolve => setTimeout(resolve, waitTime));
        
        // Reset phases for retry
        extractionPhases = extractionPhases.map(phase => ({
          ...phase,
          status: 'waiting',
          progress: 0,
          data: null,
          confidence: 0
        }));
      }
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
      if (timeoutId) {
        clearTimeout(timeoutId);
        timeoutId = null;
      }
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
      
      // Calculate overall progress based on completed phases
      const completedPhases = extractionPhases.filter(p => p.status === 'completed').length;
      const currentPhaseProgress = data.progress || 0;
      overallProgress = Math.round(((completedPhases * 100) + currentPhaseProgress) / extractionPhases.length);
      
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
    if (timeoutId) {
      clearTimeout(timeoutId);
      timeoutId = null;
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
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
  });
</script>

<div class="multimodal-extraction">
  <!-- Compact Animated Progress Header -->
  <div class="cooking-header">
    <div class="cooking-animation">
      {#if isExtracting}
        <!-- Show modern spinner when extracting -->
        <div class="cooking-spinner">
          <Loading 
            size="md"
            message=""
          />
        </div>
      {:else}
        <!-- Show simple ready state icon when idle -->
        <div class="ready-icon">🍴</div>
      {/if}
    </div>
    <div class="cooking-title">
      <h3>AI Recipe Extraction</h3>
      <p class="cooking-subtitle">
        {#if isExtracting}
          Extracting delicious recipe details... {overallProgress}%
        {:else}
          Ready to transform your Instagram post into a recipe!
        {/if}
      </p>
    </div>
  </div>
  
  <!-- Compact Progress Bar -->
  {#if isExtracting}
    <div class="compact-progress">
      <div class="progress-bar-modern">
        <div 
          class="progress-fill-animated" 
          style="width: {overallProgress}%"
        ></div>
        <div class="progress-text">{overallProgress}%</div>
      </div>
      <div class="current-step">
        <span class="step-icon">{extractionPhases[currentPhase - 1]?.icon}</span>
        <span class="step-text">{extractionPhases[currentPhase - 1]?.name}</span>
        <span class="step-time">({extractionPhases[currentPhase - 1]?.estimatedTime})</span>
      </div>
    </div>
  {/if}
  
  <!-- Compact Phase Indicators (Only show when extracting) -->
  {#if isExtracting}
    <div class="phase-indicators">
      {#each extractionPhases as phase, index}
        <div class="phase-dot {getPhaseStatusClass(phase)} {currentPhase === phase.phase ? 'active' : ''}">
          <div class="phase-icon-small">{phase.icon}</div>
          <div class="phase-tooltip">
            <div class="tooltip-title">{phase.name}</div>
            <div class="tooltip-time">{phase.estimatedTime}</div>
            {#if phase.status === 'processing'}
              <div class="tooltip-progress">{phase.progress}%</div>
            {:else if phase.status === 'completed' && phase.confidence}
              <div class="tooltip-confidence">{(phase.confidence * 100).toFixed(0)}% confidence</div>
            {/if}
          </div>
        </div>
      {/each}
    </div>
  {/if}
  
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
    max-width: 600px;
    margin: 0 auto;
    padding: 24px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  }
  
  /* Cooking Header Styles */
  .cooking-header {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 16px;
    color: white;
    margin-bottom: 24px;
  }
  
  .cooking-animation {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .ready-icon {
    font-size: 2rem;
    opacity: 0.8;
    transition: opacity 0.3s ease;
  }
  
  .lottie-cooking {
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  :global(.cooking-lottie) {
    filter: drop-shadow(0 2px 4px rgba(255, 255, 255, 0.3));
  }
  
  .cooking-title h3 {
    margin: 0 0 4px 0;
    font-size: 1.5rem;
    font-weight: 700;
  }
  
  .cooking-subtitle {
    margin: 0;
    font-size: 0.9rem;
    opacity: 0.9;
  }
  
  /* Compact Progress Styles */
  .compact-progress {
    margin-bottom: 20px;
  }
  
  .progress-bar-modern {
    position: relative;
    height: 12px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 6px;
    overflow: hidden;
    margin-bottom: 12px;
  }
  
  .progress-fill-animated {
    height: 100%;
    background: linear-gradient(90deg, #10b981, #34d399, #6ee7b7);
    border-radius: 6px;
    transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    animation: shimmer 2s infinite;
  }
  
  .progress-text {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 10px;
    font-weight: 600;
    color: white;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
  }
  
  .current-step {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.9rem;
    color: #374151;
    background: white;
    padding: 8px 12px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
  
  .step-icon {
    font-size: 1.2rem;
  }
  
  .step-text {
    font-weight: 600;
  }
  
  .step-time {
    font-size: 0.8rem;
    color: #6b7280;
  }
  
  /* Phase Indicators */
  .phase-indicators {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
    position: relative;
  }
  
  .phase-indicators::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 10%;
    right: 10%;
    height: 2px;
    background: #e5e7eb;
    z-index: 1;
  }
  
  .phase-dot {
    position: relative;
    z-index: 2;
    width: 48px;
    height: 48px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f3f4f6;
    border: 3px solid #e5e7eb;
    transition: all 0.3s ease;
    cursor: pointer;
  }
  
  .phase-dot.phase-waiting {
    background: #f9fafb;
    border-color: #d1d5db;
  }
  
  .phase-dot.phase-processing {
    background: #fef3c7;
    border-color: #f59e0b;
    animation: pulse 2s infinite;
    box-shadow: 0 0 0 4px rgba(245, 158, 11, 0.2);
  }
  
  .phase-dot.phase-completed {
    background: #dcfce7;
    border-color: #22c55e;
    box-shadow: 0 2px 8px rgba(34, 197, 94, 0.3);
  }
  
  .phase-dot.phase-failed {
    background: #fee2e2;
    border-color: #ef4444;
  }
  
  .phase-dot.active {
    transform: scale(1.1);
  }
  
  .phase-icon-small {
    font-size: 1.2rem;
  }
  
  /* Tooltip Styles */
  .phase-tooltip {
    position: absolute;
    bottom: 120%;
    left: 50%;
    transform: translateX(-50%);
    background: #1f2937;
    color: white;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 0.75rem;
    white-space: nowrap;
    opacity: 0;
    visibility: hidden;
    transition: all 0.2s ease;
    z-index: 10;
  }
  
  .phase-tooltip::after {
    content: '';
    position: absolute;
    top: 100%;
    left: 50%;
    transform: translateX(-50%);
    border: 4px solid transparent;
    border-top-color: #1f2937;
  }
  
  .phase-dot:hover .phase-tooltip {
    opacity: 1;
    visibility: visible;
  }
  
  .tooltip-title {
    font-weight: 600;
    margin-bottom: 2px;
  }
  
  .tooltip-time, .tooltip-progress, .tooltip-confidence {
    font-size: 0.65rem;
    opacity: 0.8;
  }
  
  /* Button Styles */
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
  
  /* Error Message Styles */
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
  
  /* Final Results Styles */
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
  
  /* Animations */
  @keyframes bounce {
    0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
    40% { transform: translateY(-10px); }
    60% { transform: translateY(-5px); }
  }
  
  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-2px); }
    75% { transform: translateX(2px); }
  }
  
  @keyframes shimmer {
    0% { background-position: -200px 0; }
    100% { background-position: 200px 0; }
  }
  
  @keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.05); opacity: 0.8; }
  }
  
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
  
  /* Media Queries */
  @media (max-width: 640px) {
    .multimodal-extraction {
      padding: 16px;
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