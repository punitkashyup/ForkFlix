import asyncio
import tempfile
import os
import logging
import re
import io
from typing import Dict, Any, List, Optional, Tuple, Union
import httpx
import subprocess
from pathlib import Path
import time

logger = logging.getLogger(__name__)


class ProductionAudioProcessor:
    """
    Production-level audio processing for recipe extraction from Instagram videos
    
    Features:
    - Multiple audio extraction methods (moviepy, pydub, direct extraction)
    - Robust Whisper transcription with model management
    - Advanced cooking instruction extraction with NLP
    - Smart confidence scoring and quality validation
    - Comprehensive error handling and fallbacks
    - Audio format optimization and validation
    """
    
    def __init__(self):
        self.client = None
        self.whisper_model = None
        self.whisper_model_size = "base"  # base, small, medium, large
        self.supported_formats = ['.mp4', '.mov', '.avi', '.mkv', '.webm']
        
        # Audio processing configuration
        self.audio_config = {
            'sample_rate': 16000,  # Whisper optimal sample rate
            'channels': 1,         # Mono for speech recognition
            'format': 'wav',       # Standard format
            'bit_depth': 16        # Standard bit depth
        }
        
        # Cooking-specific vocabulary for enhanced recognition
        self.cooking_vocabulary = self._load_cooking_vocabulary()
        
    def _load_cooking_vocabulary(self) -> Dict[str, List[str]]:
        """Load cooking-specific vocabulary for enhanced recognition"""
        return {
            'actions': [
                'add', 'mix', 'stir', 'cook', 'heat', 'bake', 'fry', 'boil', 'simmer',
                'chop', 'dice', 'slice', 'mince', 'season', 'pour', 'blend', 'whisk',
                'combine', 'fold', 'grill', 'roast', 'sauté', 'steam', 'marinate',
                'garnish', 'serve', 'plate', 'drizzle', 'sprinkle', 'toss', 'caramelize',
                'braise', 'sear', 'poach', 'blanch', 'reduce', 'deglaze', 'julienne'
            ],
            'ingredients': [
                'salt', 'pepper', 'oil', 'butter', 'garlic', 'onion', 'tomato', 'cheese',
                'chicken', 'beef', 'pork', 'fish', 'pasta', 'rice', 'flour', 'sugar',
                'eggs', 'milk', 'cream', 'herbs', 'spices', 'vegetables', 'fruits',
                'lemon', 'lime', 'vinegar', 'wine', 'stock', 'broth', 'sauce'
            ],
            'equipment': [
                'pan', 'pot', 'oven', 'stove', 'microwave', 'blender', 'mixer',
                'knife', 'cutting board', 'bowl', 'spatula', 'whisk', 'ladle',
                'skillet', 'saucepan', 'baking sheet', 'casserole', 'grill'
            ],
            'measurements': [
                'cup', 'cups', 'tablespoon', 'tablespoons', 'teaspoon', 'teaspoons',
                'ounce', 'ounces', 'pound', 'pounds', 'gram', 'grams', 'liter', 'liters',
                'pinch', 'dash', 'handful', 'clove', 'cloves'
            ],
            'time_units': [
                'minute', 'minutes', 'second', 'seconds', 'hour', 'hours',
                'mins', 'secs', 'hrs'
            ]
        }
    
    async def transcribe_video_audio(self, video_url: str) -> Dict[str, Any]:
        """
        Production-level audio transcription from Instagram videos
        
        Returns comprehensive audio analysis including:
        - Full transcription with confidence scores
        - Extracted cooking instructions
        - Time indicators and measurements
        - Cooking vocabulary analysis
        - Audio quality metrics
        """
        start_time = time.time()
        
        try:
            logger.info(f"🎤 Starting production audio processing for: {video_url}")
            
            # Step 1: Extract audio with multiple fallback methods
            audio_path = await self._extract_audio_robust(video_url)
            if not audio_path:
                return self._create_failed_result("Audio extraction failed")
            
            # Step 2: Validate and optimize audio quality
            audio_metrics = await self._validate_audio_quality(audio_path)
            if audio_metrics['quality_score'] < 0.3:
                logger.warning(f"Low audio quality detected: {audio_metrics['quality_score']:.2f}")
            
            # Step 3: Transcribe with Whisper
            transcription_result = await self._transcribe_with_whisper_robust(audio_path)
            if not transcription_result['success']:
                return self._create_failed_result("Transcription failed")
            
            # Step 4: Extract cooking-specific information
            cooking_analysis = await self._analyze_cooking_content(
                transcription_result['text'],
                transcription_result.get('segments', [])
            )
            
            # Step 5: Generate comprehensive instructions
            instructions = await self._generate_cooking_instructions(
                transcription_result['text'],
                cooking_analysis
            )
            
            # Step 6: Calculate overall confidence
            confidence = self._calculate_comprehensive_confidence(
                transcription_result,
                cooking_analysis,
                audio_metrics
            )
            
            # Clean up temporary files
            try:
                os.unlink(audio_path)
                logger.info("🧹 Audio file cleaned up")
            except:
                pass
            
            processing_time = time.time() - start_time
            
            result = {
                "transcription": transcription_result['text'],
                "transcription_confidence": float(transcription_result.get('confidence', 0.5)),
                "instructions": instructions,
                "raw_instructions": cooking_analysis['instructions'],
                "confidence": float(confidence),
                "cooking_terms_found": cooking_analysis['cooking_terms_count'],
                "time_indicators": self._make_json_serializable(cooking_analysis['time_indicators']),
                "measurements": self._make_json_serializable(cooking_analysis['measurements']),
                "ingredients_mentioned": cooking_analysis['ingredients'],
                "cooking_actions": cooking_analysis['actions'],
                "audio_quality": self._make_json_serializable(audio_metrics),
                "processing_time": round(processing_time, 2),
                "segments": self._make_json_serializable(transcription_result.get('segments', [])),
                "success": True
            }
            
            logger.info(f"✅ Audio processing completed in {processing_time:.1f}s with confidence {confidence:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Audio processing failed: {e}")
            return self._create_failed_result(f"Processing error: {str(e)}")
    
    async def _extract_audio_robust(self, video_url: str) -> Optional[str]:
        """Extract audio using multiple fallback methods"""
        
        # Method 1: Try imageio-ffmpeg (bundled FFmpeg)
        audio_path = await self._extract_audio_imageio(video_url)
        if audio_path:
            logger.info("✅ Audio extracted using imageio-ffmpeg")
            return audio_path
        
        # Method 2: Try moviepy (most reliable)
        audio_path = await self._extract_audio_moviepy(video_url)
        if audio_path:
            logger.info("✅ Audio extracted using moviepy")
            return audio_path
        
        # Method 3: Try pydub
        audio_path = await self._extract_audio_pydub(video_url)
        if audio_path:
            logger.info("✅ Audio extracted using pydub")
            return audio_path
        
        # Method 4: Try direct FFmpeg (if available)
        audio_path = await self._extract_audio_ffmpeg(video_url)
        if audio_path:
            logger.info("✅ Audio extracted using FFmpeg")
            return audio_path
        
        logger.error("❌ All audio extraction methods failed")
        return None
    
    async def _extract_audio_imageio(self, video_url: str) -> Optional[str]:
        """Extract audio using imageio-ffmpeg (bundled FFmpeg)"""
        try:
            import imageio_ffmpeg
            import subprocess
            import numpy as np
            from scipy.io import wavfile
            
            # Download video first
            video_path = await self._download_video_temp(video_url)
            if not video_path:
                return None
            
            # Create unique audio output path
            timestamp = int(time.time() * 1000)
            audio_path = f"/tmp/audio_imageio_{timestamp}.wav"
            
            logger.info("🎬 Extracting audio using imageio-ffmpeg...")
            
            # Get the bundled FFmpeg executable
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            
            def extract_sync():
                # Use imageio-ffmpeg's bundled FFmpeg
                cmd = [
                    ffmpeg_exe, '-i', video_path,
                    '-acodec', 'pcm_s16le',  # 16-bit PCM
                    '-ar', str(self.audio_config['sample_rate']),  # Sample rate
                    '-ac', str(self.audio_config['channels']),     # Mono
                    '-y',  # Overwrite output
                    audio_path
                ]
                
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False
                )
                
                return result.returncode == 0
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(None, extract_sync)
            
            # Clean up video file
            try:
                os.unlink(video_path)
            except:
                pass
            
            if success and os.path.exists(audio_path) and os.path.getsize(audio_path) > 1000:
                return audio_path
            else:
                if os.path.exists(audio_path):
                    os.unlink(audio_path)
                return None
                
        except Exception as e:
            logger.warning(f"imageio-ffmpeg audio extraction failed: {e}")
            return None
    
    async def _extract_audio_moviepy(self, video_url: str) -> Optional[str]:
        """Extract audio using moviepy"""
        try:
            from moviepy.editor import VideoFileClip
            
            # Download video first
            video_path = await self._download_video_temp(video_url)
            if not video_path:
                return None
            
            # Create unique audio output path
            timestamp = int(time.time() * 1000)
            audio_path = f"/tmp/audio_moviepy_{timestamp}.wav"
            
            # Extract audio using moviepy
            logger.info("🎬 Extracting audio using moviepy...")
            
            def extract_sync():
                with VideoFileClip(video_path) as video:
                    if video.audio is not None:
                        video.audio.write_audiofile(
                            audio_path,
                            fps=self.audio_config['sample_rate'],
                            nbytes=2,  # 16-bit
                            verbose=False,
                            logger=None
                        )
                        return True
                return False
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(None, extract_sync)
            
            # Clean up video file
            try:
                os.unlink(video_path)
            except:
                pass
            
            if success and os.path.exists(audio_path) and os.path.getsize(audio_path) > 1000:
                return audio_path
            else:
                if os.path.exists(audio_path):
                    os.unlink(audio_path)
                return None
                
        except Exception as e:
            logger.warning(f"Moviepy audio extraction failed: {e}")
            return None
    
    async def _extract_audio_pydub(self, video_url: str) -> Optional[str]:
        """Extract audio using pydub"""
        try:
            from pydub import AudioSegment
            
            # Download video first
            video_path = await self._download_video_temp(video_url)
            if not video_path:
                return None
            
            # Create unique audio output path
            timestamp = int(time.time() * 1000)
            audio_path = f"/tmp/audio_pydub_{timestamp}.wav"
            
            logger.info("🔊 Extracting audio using pydub...")
            
            def extract_sync():
                # Load video and extract audio
                audio = AudioSegment.from_file(video_path)
                
                # Convert to optimal format for Whisper
                audio = audio.set_frame_rate(self.audio_config['sample_rate'])
                audio = audio.set_channels(self.audio_config['channels'])
                audio = audio.set_sample_width(2)  # 16-bit
                
                # Export as WAV
                audio.export(audio_path, format="wav")
                return True
            
            # Run in thread pool
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(None, extract_sync)
            
            # Clean up video file
            try:
                os.unlink(video_path)
            except:
                pass
            
            if success and os.path.exists(audio_path) and os.path.getsize(audio_path) > 1000:
                return audio_path
            else:
                if os.path.exists(audio_path):
                    os.unlink(audio_path)
                return None
                
        except Exception as e:
            logger.warning(f"Pydub audio extraction failed: {e}")
            return None
    
    async def _extract_audio_ffmpeg(self, video_url: str) -> Optional[str]:
        """Extract audio using FFmpeg directly"""
        try:
            # Check if FFmpeg is available
            result = subprocess.run(['which', 'ffmpeg'], capture_output=True, text=True)
            if result.returncode != 0:
                logger.info("FFmpeg not available, skipping")
                return None
            
            # Download video first
            video_path = await self._download_video_temp(video_url)
            if not video_path:
                return None
            
            # Create unique audio output path
            timestamp = int(time.time() * 1000)
            audio_path = f"/tmp/audio_ffmpeg_{timestamp}.wav"
            
            logger.info("🛠️ Extracting audio using FFmpeg...")
            
            # FFmpeg command for optimal audio extraction
            cmd = [
                'ffmpeg', '-i', video_path,
                '-acodec', 'pcm_s16le',  # 16-bit PCM
                '-ar', str(self.audio_config['sample_rate']),  # Sample rate
                '-ac', str(self.audio_config['channels']),     # Mono
                '-y',  # Overwrite output
                audio_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Clean up video file
            try:
                os.unlink(video_path)
            except:
                pass
            
            if process.returncode == 0 and os.path.exists(audio_path) and os.path.getsize(audio_path) > 1000:
                return audio_path
            else:
                logger.warning(f"FFmpeg failed: {stderr.decode()}")
                if os.path.exists(audio_path):
                    os.unlink(audio_path)
                return None
                
        except Exception as e:
            logger.warning(f"FFmpeg audio extraction failed: {e}")
            return None
    
    async def _download_video_temp(self, video_url: str) -> Optional[str]:
        """Download video using the same method as video processor"""
        try:
            import time
            timestamp = int(time.time() * 1000)
            output_path = f"/tmp/video_audio_{timestamp}.mp4"
            
            # For Instagram URLs, use yt-dlp
            if 'instagram.com' in video_url:
                return await self._download_instagram_video_ytdlp(video_url, output_path)
            else:
                # For other URLs, use direct download
                return await self._download_video_direct(video_url, output_path)
                
        except Exception as e:
            logger.error(f"Video download failed: {e}")
            return None
    
    async def _download_instagram_video_ytdlp(self, instagram_url: str, output_path: str) -> Optional[str]:
        """Download Instagram video using yt-dlp"""
        try:
            import yt_dlp
            
            # Configure yt-dlp options
            ydl_opts = {
                'outtmpl': output_path,
                'quiet': True,
                'no_warnings': True,
                'format': 'best[height<=720]/best',
                'noplaylist': True,
                'extract_flat': False,
                'writesubtitles': False,
                'writeautomaticsub': False,
                'ignoreerrors': False,
                'merge_output_format': 'mp4',
                'overwrites': True,
                'force_overwrites': True,
            }
            
            # Run yt-dlp in a separate thread
            loop = asyncio.get_event_loop()
            
            def download_sync():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([instagram_url])
            
            await loop.run_in_executor(None, download_sync)
            
            # Verify file exists and has content
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                return output_path
            else:
                if os.path.exists(output_path):
                    os.unlink(output_path)
                return None
                
        except Exception as e:
            logger.error(f"Instagram video download failed: {e}")
            if os.path.exists(output_path):
                try:
                    os.unlink(output_path)
                except:
                    pass
            return None
    
    async def _download_video_direct(self, video_url: str, output_path: str) -> Optional[str]:
        """Download video directly via HTTP"""
        try:
            if not self.client:
                self.client = httpx.AsyncClient(timeout=120.0)
            
            response = await self.client.get(video_url)
            if response.status_code != 200:
                return None
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            return output_path if os.path.exists(output_path) and os.path.getsize(output_path) > 0 else None
                
        except Exception as e:
            logger.error(f"Direct video download failed: {e}")
            return None
    
    async def _validate_audio_quality(self, audio_path: str) -> Dict[str, Any]:
        """Validate audio quality and return metrics"""
        try:
            import librosa
            import numpy as np
            
            # Load audio file
            y, sr = librosa.load(audio_path, sr=None)
            
            # Calculate quality metrics
            duration = len(y) / sr
            rms_energy = np.sqrt(np.mean(y**2))
            zero_crossing_rate = np.mean(librosa.feature.zero_crossing_rate(y))
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
            
            # Calculate signal-to-noise ratio estimate
            signal_power = np.mean(y**2)
            noise_estimate = np.var(y[:min(1000, len(y))])  # Estimate from beginning
            snr_estimate = 10 * np.log10(signal_power / max(noise_estimate, 1e-10))
            
            # Quality score (0-1)
            quality_factors = [
                min(duration / 5.0, 1.0),  # Prefer longer audio
                min(rms_energy * 10, 1.0),  # Prefer audible audio
                min(snr_estimate / 20.0, 1.0),  # Prefer clean audio
                1.0 if sr >= 16000 else sr / 16000  # Prefer good sample rate
            ]
            
            quality_score = np.mean(quality_factors)
            
            return {
                'duration': round(duration, 2),
                'sample_rate': sr,
                'rms_energy': round(rms_energy, 4),
                'snr_estimate': round(snr_estimate, 2),
                'quality_score': round(quality_score, 3),
                'channels': 1 if len(y.shape) == 1 else y.shape[1]
            }
            
        except Exception as e:
            logger.warning(f"Audio quality validation failed: {e}")
            return {
                'duration': 0,
                'sample_rate': 0,
                'quality_score': 0.5,  # Default moderate quality
                'error': str(e)
            }
    
    async def _transcribe_with_whisper_robust(self, audio_path: str) -> Dict[str, Any]:
        """Robust Whisper transcription with model management"""
        try:
            import whisper
            
            # Load Whisper model if not already loaded
            if self.whisper_model is None:
                logger.info(f"🤖 Loading Whisper {self.whisper_model_size} model...")
                self.whisper_model = whisper.load_model(self.whisper_model_size)
            
            # Transcribe with detailed options
            logger.info("🎯 Starting Whisper transcription...")
            
            def transcribe_sync():
                return self.whisper_model.transcribe(
                    audio_path,
                    language='en',  # Assume English for cooking videos
                    task='transcribe',
                    fp16=False,  # Better compatibility
                    verbose=False
                )
            
            # Run in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, transcribe_sync)
            
            # Extract key information
            text = result.get("text", "").strip()
            language = result.get("language", "unknown")
            segments = result.get("segments", [])
            
            # Calculate transcription confidence
            segment_confidences = []
            for segment in segments:
                if 'confidence' in segment:
                    segment_confidences.append(segment['confidence'])
                elif 'words' in segment:
                    word_confidences = [w.get('confidence', 0.5) for w in segment['words'] if 'confidence' in w]
                    if word_confidences:
                        segment_confidences.append(np.mean(word_confidences))
            
            avg_confidence = np.mean(segment_confidences) if segment_confidences else 0.7
            
            logger.info(f"✅ Whisper transcription completed. Language: {language}, "
                       f"Text length: {len(text)}, Confidence: {avg_confidence:.3f}")
            
            return {
                'success': True,
                'text': text,
                'language': language,
                'segments': segments,
                'confidence': avg_confidence,
                'word_count': len(text.split()) if text else 0
            }
            
        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            return {
                'success': False,
                'text': "",
                'error': str(e),
                'confidence': 0.1
            }
    
    async def _analyze_cooking_content(self, text: str, segments: List[Dict]) -> Dict[str, Any]:
        """Analyze transcription for cooking-specific content"""
        
        text_lower = text.lower()
        
        # Extract cooking actions
        actions_found = []
        for action in self.cooking_vocabulary['actions']:
            if action in text_lower:
                actions_found.append(action)
        
        # Extract ingredients mentioned
        ingredients_found = []
        for ingredient in self.cooking_vocabulary['ingredients']:
            if ingredient in text_lower:
                ingredients_found.append(ingredient)
        
        # Extract measurements
        measurements = self._extract_measurements(text)
        
        # Extract time indicators
        time_indicators = self._extract_time_indicators_advanced(text, segments)
        
        # Extract cooking instructions
        instructions = self._extract_cooking_instructions_advanced(text, segments)
        
        # Count cooking-related terms
        all_cooking_terms = (
            self.cooking_vocabulary['actions'] + 
            self.cooking_vocabulary['ingredients'] + 
            self.cooking_vocabulary['equipment']
        )
        
        cooking_terms_count = sum(1 for term in all_cooking_terms if term in text_lower)
        
        return {
            'actions': list(set(actions_found)),
            'ingredients': list(set(ingredients_found)),
            'measurements': measurements,
            'time_indicators': time_indicators,
            'instructions': instructions,
            'cooking_terms_count': cooking_terms_count,
            'cooking_density': cooking_terms_count / max(len(text.split()), 1)
        }
    
    def _extract_measurements(self, text: str) -> List[Dict[str, Any]]:
        """Extract cooking measurements from text"""
        measurements = []
        
        # Patterns for measurements
        patterns = [
            (r'(\d+(?:\.\d+)?)\s*(cup|cups)', 'volume'),
            (r'(\d+(?:\.\d+)?)\s*(tablespoon|tablespoons|tbsp)', 'volume'),
            (r'(\d+(?:\.\d+)?)\s*(teaspoon|teaspoons|tsp)', 'volume'),
            (r'(\d+(?:\.\d+)?)\s*(ounce|ounces|oz)', 'weight'),
            (r'(\d+(?:\.\d+)?)\s*(pound|pounds|lb|lbs)', 'weight'),
            (r'(\d+(?:\.\d+)?)\s*(gram|grams|g)', 'weight'),
            (r'(\d+(?:\.\d+)?)\s*(kilogram|kilograms|kg)', 'weight'),
            (r'(\d+(?:\.\d+)?)\s*(liter|liters|l)', 'volume'),
            (r'(\d+(?:\.\d+)?)\s*(milliliter|milliliters|ml)', 'volume'),
        ]
        
        text_lower = text.lower()
        
        for pattern, unit_type in patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                try:
                    amount = float(match.group(1))
                    unit = match.group(2)
                    measurements.append({
                        'amount': amount,
                        'unit': unit,
                        'type': unit_type,
                        'text': match.group(0)
                    })
                except ValueError:
                    continue
        
        return measurements
    
    def _extract_time_indicators_advanced(self, text: str, segments: List[Dict]) -> List[Dict[str, Any]]:
        """Extract time indicators with segment timing"""
        time_indicators = []
        
        # Enhanced time patterns
        patterns = [
            (r'(\d+)\s*(minute|minutes|mins?)', 'duration', 'minutes'),
            (r'(\d+)\s*(second|seconds|secs?)', 'duration', 'seconds'),
            (r'(\d+)\s*(hour|hours|hrs?)', 'duration', 'hours'),
            (r'for\s+(\d+)\s*(minute|minutes|mins?)', 'cooking_time', 'minutes'),
            (r'cook\s+for\s+(\d+)', 'cooking_time', 'minutes'),
            (r'bake\s+for\s+(\d+)', 'baking_time', 'minutes'),
            (r'until\s+(golden|brown|tender|crispy|done)', 'condition', None),
            (r'about\s+(\d+)\s*(minute|minutes)', 'approximate', 'minutes'),
            (r'around\s+(\d+)\s*(minute|minutes)', 'approximate', 'minutes'),
        ]
        
        text_lower = text.lower()
        
        for pattern, indicator_type, unit in patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                try:
                    if indicator_type == 'condition':
                        time_indicators.append({
                            'type': indicator_type,
                            'condition': match.group(1),
                            'text': match.group(0),
                            'position': match.start()
                        })
                    else:
                        value = int(match.group(1))
                        time_indicators.append({
                            'type': indicator_type,
                            'value': value,
                            'unit': unit,
                            'text': match.group(0),
                            'position': match.start()
                        })
                except (ValueError, IndexError):
                    continue
        
        return time_indicators
    
    def _extract_cooking_instructions_advanced(self, text: str, segments: List[Dict]) -> List[str]:
        """Extract cooking instructions with advanced NLP"""
        instructions = []
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:  # Skip very short sentences
                continue
            
            sentence_lower = sentence.lower()
            
            # Check if sentence contains cooking context
            has_cooking_action = any(action in sentence_lower for action in self.cooking_vocabulary['actions'])
            has_cooking_ingredient = any(ingredient in sentence_lower for ingredient in self.cooking_vocabulary['ingredients'])
            has_time_reference = any(unit in sentence_lower for unit in self.cooking_vocabulary['time_units'])
            has_measurement = bool(re.search(r'\\d+\\s*(cup|tablespoon|teaspoon|ounce|pound)', sentence_lower))
            
            # Score sentence for cooking relevance
            cooking_score = 0
            if has_cooking_action:
                cooking_score += 2
            if has_cooking_ingredient:
                cooking_score += 1
            if has_time_reference:
                cooking_score += 1
            if has_measurement:
                cooking_score += 1
            
            # Include if cooking-relevant
            if cooking_score >= 2:
                # Clean up and format
                clean_sentence = sentence.strip().capitalize()
                if not clean_sentence.endswith('.'):
                    clean_sentence += '.'
                instructions.append(clean_sentence)
        
        return instructions[:10]  # Limit to 10 most relevant instructions
    
    async def _generate_cooking_instructions(self, text: str, cooking_analysis: Dict) -> str:
        """Generate formatted cooking instructions"""
        if not cooking_analysis['instructions']:
            return "No specific cooking instructions detected in audio."
        
        # Number the instructions
        numbered_instructions = []
        for i, instruction in enumerate(cooking_analysis['instructions'], 1):
            numbered_instructions.append(f"{i}. {instruction}")
        
        result = '\\n'.join(numbered_instructions)
        
        # Add cooking tips based on analysis
        tips = []
        if cooking_analysis['time_indicators']:
            tips.append("⏱️ Pay attention to timing mentioned in the video")
        if cooking_analysis['measurements']:
            tips.append("📏 Use precise measurements as indicated")
        if len(cooking_analysis['actions']) >= 5:
            tips.append("👨‍🍳 Multiple cooking techniques are used in this recipe")
        
        if tips:
            result += '\\n\\nCooking Tips:\\n' + '\\n'.join(f"• {tip}" for tip in tips)
        
        return result
    
    def _calculate_comprehensive_confidence(
        self, 
        transcription_result: Dict,
        cooking_analysis: Dict,
        audio_metrics: Dict
    ) -> float:
        """Calculate comprehensive confidence score"""
        
        confidence = 0.3  # Base confidence
        
        # Transcription quality
        transcription_conf = transcription_result.get('confidence', 0.5)
        confidence += transcription_conf * 0.3
        
        # Audio quality
        audio_quality = audio_metrics.get('quality_score', 0.5)
        confidence += audio_quality * 0.2
        
        # Cooking content density
        cooking_density = cooking_analysis.get('cooking_density', 0)
        confidence += min(cooking_density * 2, 0.2)
        
        # Number of cooking elements found
        elements_score = 0
        if cooking_analysis['actions']:
            elements_score += 0.05
        if cooking_analysis['ingredients']:
            elements_score += 0.05
        if cooking_analysis['time_indicators']:
            elements_score += 0.05
        if cooking_analysis['measurements']:
            elements_score += 0.05
        if cooking_analysis['instructions']:
            elements_score += 0.1
        
        confidence += elements_score
        
        # Text length bonus (longer transcription usually better)
        text_length = transcription_result.get('word_count', 0)
        if text_length > 50:
            confidence += 0.1
        elif text_length > 20:
            confidence += 0.05
        
        return min(confidence, 0.95)  # Cap at 95%
    
    def _make_json_serializable(self, obj):
        """Convert numpy types to JSON-serializable Python types"""
        import numpy as np
        
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.int64, np.int32, np.int16, np.int8)):
            return int(obj)
        elif isinstance(obj, (np.float64, np.float32, np.float16)):
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, dict):
            return {key: self._make_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._make_json_serializable(item) for item in obj]
        else:
            return obj
    
    def _create_failed_result(self, error_message: str) -> Dict[str, Any]:
        """Create a standardized failed result"""
        return {
            "transcription": "",
            "transcription_confidence": 0.1,
            "instructions": "",
            "raw_instructions": [],
            "confidence": 0.1,
            "cooking_terms_found": 0,
            "time_indicators": [],
            "measurements": [],
            "ingredients_mentioned": [],
            "cooking_actions": [],
            "audio_quality": {"quality_score": 0.0},
            "processing_time": 0,
            "segments": [],
            "success": False,
            "error": error_message
        }
    
    async def close(self):
        """Close HTTP client and clean up resources"""
        if self.client:
            await self.client.aclose()
        
        # Optionally unload Whisper model to free memory
        if self.whisper_model is not None:
            del self.whisper_model
            self.whisper_model = None


# Global instance
production_audio_processor = ProductionAudioProcessor()