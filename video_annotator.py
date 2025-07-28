#!/usr/bin/env python3
"""
Video Segment Annotator
A GUI tool for video annotation, segmentation, and dataset creation.

Author: Video Annotation Tools
License: MIT
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import cv2
import os
import json
import shutil
from pathlib import Path
from PIL import Image, ImageTk
import threading
import time

class VideoSegmentAnnotator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Video Segment Annotator")
        self.root.geometry("1200x800")  # More reasonable window size
        
        # Video variables
        self.cap = None
        self.current_video_path = None
        self.video_files = []
        self.current_video_index = 0
        self.is_playing = False
        self.current_frame = 0
        self.total_frames = 0
        self.fps = 30
        self.video_duration = 0
        
        # Annotation variables
        self.segments = []  # List of (start_time, end_time) tuples
        self.temp_start_time = None
        
        # UI variables
        self.video_label = None
        self.progress_var = None
        self.time_var = None
        
        # Project paths
        self.project_dir = Path(__file__).parent
        self.videos_dir = self.project_dir / "videos"
        self.segments_dir = self.project_dir / "segments"
        self.unified_dataset_dir = self.project_dir / "unified_dataset"
        
        self.setup_directories()
        self.setup_ui()
        self.load_videos()
        
    def setup_directories(self):
        """Create necessary directories"""
        self.videos_dir.mkdir(exist_ok=True)
        self.segments_dir.mkdir(exist_ok=True)
        (self.segments_dir / "videos").mkdir(exist_ok=True)
        (self.segments_dir / "frames").mkdir(exist_ok=True)
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for responsive layout
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)  # Video display gets weight
        
        # Title
        title_label = ttk.Label(main_frame, text="Video Segment Annotator", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=1, pady=(0, 10))
        
        # Video info frame
        info_frame = ttk.LabelFrame(main_frame, text="Video Information", padding="5")
        info_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.video_info_label = ttk.Label(info_frame, text="No videos found. Place video files in the 'videos' folder.")
        self.video_info_label.grid(row=0, column=0, sticky=tk.W)
        
        # Video display frame with fixed height
        video_frame = ttk.LabelFrame(main_frame, text="Video Player", padding="5")
        video_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        video_frame.columnconfigure(0, weight=1)
        video_frame.rowconfigure(0, weight=1)
        
        # Set minimum height for video frame
        self.video_label = ttk.Label(video_frame, text="No video loaded", anchor="center",
                                   background="black", foreground="white")
        self.video_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Limit video frame height
        video_frame.grid_propagate(False)
        video_frame.config(height=400)
        
        # Controls frame
        controls_frame = ttk.LabelFrame(main_frame, text="Video Controls", padding="5")
        controls_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Video navigation buttons
        nav_frame = ttk.Frame(controls_frame)
        nav_frame.grid(row=0, column=0, columnspan=1, pady=(0, 10))
        
        ttk.Button(nav_frame, text="⏮ Previous Video", command=self.previous_video).grid(row=0, column=0, padx=5)
        ttk.Button(nav_frame, text="🔄 Reload Videos", command=self.load_videos).grid(row=0, column=1, padx=5)
        ttk.Button(nav_frame, text="Next Video ⏭", command=self.next_video).grid(row=0, column=2, padx=5)
        
        # Playback controls
        play_frame = ttk.Frame(controls_frame)
        play_frame.grid(row=1, column=0, columnspan=1, pady=(0, 10))
        
        ttk.Button(play_frame, text="⏪", command=self.seek_backward, width=6).grid(row=0, column=0, padx=2)
        self.play_button = ttk.Button(play_frame, text="▶", command=self.toggle_play, width=6)
        self.play_button.grid(row=0, column=1, padx=2)
        ttk.Button(play_frame, text="⏩", command=self.seek_forward, width=6).grid(row=0, column=2, padx=2)
        
        # Progress bar
        progress_frame = ttk.Frame(controls_frame)
        progress_frame.grid(row=2, column=0, columnspan=1, sticky=(tk.W, tk.E), pady=(0, 5))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Scale(progress_frame, from_=0, to=100, orient=tk.HORIZONTAL, 
                                     variable=self.progress_var, command=self.on_progress_change)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Time display
        self.time_var = tk.StringVar(value="00:00 / 00:00")
        time_label = ttk.Label(progress_frame, textvariable=self.time_var, width=15)
        time_label.grid(row=0, column=1)
        
        # Annotation and dataset controls
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        bottom_frame.columnconfigure(1, weight=1)
        
        # Annotation controls
        annotation_frame = ttk.LabelFrame(bottom_frame, text="Segment Annotation", padding="5")
        annotation_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        ttk.Button(annotation_frame, text="📍 Mark Start", command=self.mark_start, width=15).grid(row=0, column=0, pady=2, sticky=(tk.W, tk.E))
        ttk.Button(annotation_frame, text="🏁 Mark End", command=self.mark_end, width=15).grid(row=1, column=0, pady=2, sticky=(tk.W, tk.E))
        ttk.Button(annotation_frame, text="↩️ Clear Last", command=self.clear_last_segment, width=15).grid(row=2, column=0, pady=2, sticky=(tk.W, tk.E))
        ttk.Button(annotation_frame, text="🗑️ Clear All", command=self.clear_all_segments, width=15).grid(row=3, column=0, pady=2, sticky=(tk.W, tk.E))
        
        # Segments list
        segments_frame = ttk.LabelFrame(bottom_frame, text="Marked Segments", padding="5")
        segments_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        segments_frame.columnconfigure(0, weight=1)
        segments_frame.rowconfigure(0, weight=1)
        
        # Create treeview for segments with fixed height
        self.segments_tree = ttk.Treeview(segments_frame, columns=("start", "end", "duration"), show="headings", height=4)
        self.segments_tree.heading("start", text="Start Time")
        self.segments_tree.heading("end", text="End Time") 
        self.segments_tree.heading("duration", text="Duration")
        self.segments_tree.column("start", width=80)
        self.segments_tree.column("end", width=80)
        self.segments_tree.column("duration", width=80)
        self.segments_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar for treeview
        segments_scrollbar = ttk.Scrollbar(segments_frame, orient=tk.VERTICAL, command=self.segments_tree.yview)
        segments_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.segments_tree.configure(yscrollcommand=segments_scrollbar.set)
        
        # Export and dataset controls
        export_frame = ttk.LabelFrame(bottom_frame, text="Export & Dataset", padding="5")
        export_frame.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Button(export_frame, text="📤 Export Segments", 
                  command=self.export_segments, width=18).grid(row=0, column=0, pady=2, sticky=(tk.W, tk.E))
        ttk.Button(export_frame, text="📊 Create Unified Dataset", 
                  command=self.create_unified_dataset, width=18).grid(row=1, column=0, pady=2, sticky=(tk.W, tk.E))
        ttk.Button(export_frame, text="📂 Open Output Folder", 
                  command=self.open_output_folder, width=18).grid(row=2, column=0, pady=2, sticky=(tk.W, tk.E))
        ttk.Button(export_frame, text="📈 View Dataset Stats", 
                  command=self.show_dataset_stats, width=18).grid(row=3, column=0, pady=2, sticky=(tk.W, tk.E))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready - Place videos in the 'videos' folder and click 'Reload Videos'")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

    def load_videos(self):
        """Load video files from the videos folder"""
        if not self.videos_dir.exists():
            self.videos_dir.mkdir(exist_ok=True)
            
        video_extensions = ['.mp4', '.avi', '.mov', '.MOV']
        self.video_files = []
        
        for ext in video_extensions:
            # Filter out hidden files (dot files)
            self.video_files.extend([f for f in self.videos_dir.glob(f'*{ext}') 
                                   if not f.name.startswith('.')])
        
        if not self.video_files:
            self.video_info_label.config(text="No videos found. Place video files (.mp4, .avi, .mov) in the 'videos' folder.")
            self.status_var.set("No videos found - add videos to the 'videos' folder")
            return
            
        self.video_files.sort()
        self.current_video_index = 0
        self.load_current_video()
        self.status_var.set(f"Loaded {len(self.video_files)} videos")
        
    def load_current_video(self):
        """Load the current video"""
        if not self.video_files:
            return
            
        if self.cap:
            self.cap.release()
            
        self.current_video_path = self.video_files[self.current_video_index]
        self.cap = cv2.VideoCapture(str(self.current_video_path))
        
        if not self.cap.isOpened():
            messagebox.showerror("Error", f"Could not open video: {self.current_video_path.name}")
            return
            
        # Get video properties
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.video_duration = self.total_frames / self.fps if self.fps > 0 else 0
        
        # Update UI
        video_info = f"Video {self.current_video_index + 1}/{len(self.video_files)}: {self.current_video_path.name} | "
        video_info += f"Duration: {self.format_time(self.video_duration)} | FPS: {self.fps:.1f} | Frames: {self.total_frames}"
        self.video_info_label.config(text=video_info)
        
        # Reset video state
        self.current_frame = 0
        self.is_playing = False
        self.segments = []
        self.temp_start_time = None
        self.play_button.config(text="▶")
        
        # Update displays
        self.update_video_display()
        self.update_segments_display()
        self.status_var.set(f"Loaded: {self.current_video_path.name}")
        
    def update_video_display(self):
        """Update the video frame display"""
        if not self.cap:
            return
            
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
        ret, frame = self.cap.read()
        
        if ret:
            # Resize frame for display - more reasonable size
            height, width = frame.shape[:2]
            display_width = 600  # Reduced from 800
            display_height = int(height * display_width / width)
            
            # Limit display height to prevent UI overflow
            max_display_height = 350
            if display_height > max_display_height:
                display_height = max_display_height
                display_width = int(width * display_height / height)
            
            frame_resized = cv2.resize(frame, (display_width, display_height))
            
            # Convert to RGB and then to PIL Image
            frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            photo = ImageTk.PhotoImage(pil_image)
            
            # Update label
            self.video_label.config(image=photo, text="")
            self.video_label.image = photo  # Keep a reference
            
        # Update progress and time
        current_time = self.current_frame / self.fps if self.fps > 0 else 0
        progress = (self.current_frame / self.total_frames * 100) if self.total_frames > 0 else 0
        
        self.progress_var.set(progress)
        self.time_var.set(f"{self.format_time(current_time)} / {self.format_time(self.video_duration)}")
        
    def format_time(self, seconds):
        """Format time in MM:SS format"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
        
    def toggle_play(self):
        """Toggle play/pause"""
        self.is_playing = not self.is_playing
        self.play_button.config(text="⏸" if self.is_playing else "▶")
        
        if self.is_playing:
            self.play_video()
            
    def play_video(self):
        """Play video in a separate thread"""
        def play_loop():
            while self.is_playing and self.current_frame < self.total_frames - 1:
                self.current_frame += 1
                self.root.after(0, self.update_video_display)
                time.sleep(1.0 / self.fps if self.fps > 0 else 1.0 / 30)
                
            if self.current_frame >= self.total_frames - 1:
                self.is_playing = False
                self.root.after(0, lambda: self.play_button.config(text="▶"))
                
        if self.is_playing:
            threading.Thread(target=play_loop, daemon=True).start()
            
    def seek_forward(self):
        """Seek forward 5 seconds"""
        skip_frames = int(5 * self.fps)
        self.current_frame = min(self.current_frame + skip_frames, self.total_frames - 1)
        self.update_video_display()
        
    def seek_backward(self):
        """Seek backward 5 seconds"""
        skip_frames = int(5 * self.fps)
        self.current_frame = max(self.current_frame - skip_frames, 0)
        self.update_video_display()
        
    def on_progress_change(self, value):
        """Handle progress bar changes"""
        if not self.is_playing:  # Only allow manual seeking when not playing
            progress = float(value)
            self.current_frame = int(progress / 100 * self.total_frames)
            self.update_video_display()
            
    def mark_start(self):
        """Mark the start of a segment"""
        current_time = self.current_frame / self.fps if self.fps > 0 else 0
        self.temp_start_time = current_time
        self.status_var.set(f"Marked start at {self.format_time(current_time)} - now mark the end")
        
    def mark_end(self):
        """Mark the end of a segment"""
        if self.temp_start_time is None:
            messagebox.showwarning("Warning", "Please mark the start time first!")
            return
            
        current_time = self.current_frame / self.fps if self.fps > 0 else 0
        
        if current_time <= self.temp_start_time:
            messagebox.showwarning("Warning", "End time must be after start time!")
            return
            
        # Add segment
        self.segments.append((self.temp_start_time, current_time))
        self.temp_start_time = None
        self.update_segments_display()
        duration = self.segments[-1][1] - self.segments[-1][0]
        self.status_var.set(f"Added segment: {self.format_time(self.segments[-1][0])} - {self.format_time(self.segments[-1][1])} (Duration: {self.format_time(duration)})")
        
    def clear_last_segment(self):
        """Clear the last marked segment"""
        if self.segments:
            removed = self.segments.pop()
            self.update_segments_display()
            self.status_var.set(f"Removed segment: {self.format_time(removed[0])} - {self.format_time(removed[1])}")
        else:
            messagebox.showinfo("Info", "No segments to remove!")
            
    def clear_all_segments(self):
        """Clear all marked segments"""
        if self.segments:
            count = len(self.segments)
            self.segments = []
            self.temp_start_time = None
            self.update_segments_display()
            self.status_var.set(f"Cleared all {count} segments")
        else:
            messagebox.showinfo("Info", "No segments to clear!")
            
    def update_segments_display(self):
        """Update the segments display"""
        # Clear existing items
        for item in self.segments_tree.get_children():
            self.segments_tree.delete(item)
            
        # Add segments
        for i, (start, end) in enumerate(self.segments):
            duration = end - start
            self.segments_tree.insert("", "end", values=(
                self.format_time(start),
                self.format_time(end),
                self.format_time(duration)
            ))
            
    def previous_video(self):
        """Load previous video"""
        if self.video_files and self.current_video_index > 0:
            self.current_video_index -= 1
            self.load_current_video()
            
    def next_video(self):
        """Load next video"""
        if self.video_files and self.current_video_index < len(self.video_files) - 1:
            self.current_video_index += 1
            self.load_current_video()
            
    def export_segments(self):
        """Export marked segments and extract frames"""
        if not self.segments:
            messagebox.showwarning("Warning", "No segments marked for export!")
            return
            
        video_name = self.current_video_path.stem
        
        try:
            for i, (start_time, end_time) in enumerate(self.segments):
                segment_name = f"{video_name}_segment_{i+1}"
                
                # Update status
                self.status_var.set(f"Exporting segment {i+1}/{len(self.segments)}...")
                self.root.update()
                
                # Create segment video
                segment_path = self.segments_dir / "videos" / f"{segment_name}.mp4"
                self.create_segment_video(start_time, end_time, segment_path)
                
                # Extract frames from segment
                segment_frames_dir = self.segments_dir / "frames" / segment_name
                self.extract_segment_frames(segment_path, segment_frames_dir, start_time, end_time)
                
            messagebox.showinfo("Success", f"Exported {len(self.segments)} segments successfully!\n\nSegment videos: segments/videos/\nExtracted frames: segments/frames/")
            self.status_var.set(f"✅ Exported {len(self.segments)} segments from {video_name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")
            self.status_var.set("❌ Export failed")
            
    def create_segment_video(self, start_time, end_time, output_path):
        """Create a video segment"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        cap = cv2.VideoCapture(str(self.current_video_path))
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Set up video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        
        # Calculate frame range
        start_frame = int(start_time * fps)
        end_frame = int(end_time * fps)
        
        # Extract frames
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        for frame_num in range(start_frame, end_frame):
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)
            
        cap.release()
        out.release()
        
    def extract_segment_frames(self, segment_path, output_dir, start_time, end_time):
        """Extract frames from a segment video"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        cap = cv2.VideoCapture(str(segment_path))
        
        if not cap.isOpened():
            raise Exception(f"Could not open segment video: {segment_path}")
            
        # Get video properties
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        # Extract frames
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            frame_name = f"frame_{frame_count+1:04d}.jpg"
            frame_path = output_dir / frame_name
            cv2.imwrite(str(frame_path), frame)
            frame_count += 1
            
        cap.release()
        
        # Save metadata
        metadata = {
            "original_video": self.current_video_path.name,
            "segment_start_time": start_time,
            "segment_end_time": end_time,
            "segment_duration": end_time - start_time,
            "fps": fps,
            "total_frames": frame_count,
            "extracted_frames": frame_count,
            "segment_video_path": str(segment_path.relative_to(self.project_dir)),
            "frames_directory": str(output_dir.relative_to(self.project_dir))
        }
        
        metadata_path = output_dir / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
            
    def create_unified_dataset(self):
        """Create a unified dataset from all extracted frames"""
        frames_dir = self.segments_dir / "frames"
        
        if not frames_dir.exists() or not list(frames_dir.iterdir()):
            messagebox.showwarning("Warning", "No extracted frames found! Please export some segments first.")
            return
            
        # Create unified dataset directories
        self.unified_dataset_dir.mkdir(exist_ok=True)
        dataset_images_dir = self.unified_dataset_dir / "images"
        dataset_metadata_dir = self.unified_dataset_dir / "metadata"
        dataset_images_dir.mkdir(exist_ok=True)
        dataset_metadata_dir.mkdir(exist_ok=True)
        
        # Get all segment folders
        segment_folders = [f for f in frames_dir.iterdir() if f.is_dir()]
        segment_folders.sort()
        
        if not segment_folders:
            messagebox.showwarning("Warning", "No segment frame folders found!")
            return
        
        self.status_var.set("Creating unified dataset...")
        self.root.update()
        
        total_frames_copied = 0
        dataset_summary = {
            "total_frames": 0,
            "total_segments": len(segment_folders),
            "creation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "segments": []
        }
        
        # Process each segment folder
        for i, segment_folder in enumerate(segment_folders):
            segment_name = segment_folder.name
            self.status_var.set(f"Processing segment {i+1}/{len(segment_folders)}: {segment_name}")
            self.root.update()
            
            # Get all frame files from this segment
            frame_files = list(segment_folder.glob("frame_*.jpg"))
            frame_files.sort()
            
            # Copy metadata if it exists
            metadata_file = segment_folder / "metadata.json"
            segment_metadata = {}
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    segment_metadata = json.load(f)
                
                # Copy metadata file with segment name
                dest_metadata_path = dataset_metadata_dir / f"{segment_name}_metadata.json"
                shutil.copy2(metadata_file, dest_metadata_path)
            
            frames_in_segment = 0
            
            # Copy each frame with unique naming
            for frame_file in frame_files:
                # Create unique frame name: segment_name + original frame name
                new_frame_name = f"{segment_name}_{frame_file.name}"
                dest_frame_path = dataset_images_dir / new_frame_name
                
                # Copy the frame with error handling
                try:
                    shutil.copy2(frame_file, dest_frame_path)
                    frames_in_segment += 1
                    total_frames_copied += 1
                except Exception as e:
                    print(f"Warning: Could not copy {frame_file.name}: {e}")
                    try:
                        shutil.copy(frame_file, dest_frame_path)
                        frames_in_segment += 1
                        total_frames_copied += 1
                    except Exception as e2:
                        print(f"Error: Could not copy {frame_file.name}: {e2}")
                        continue
            
            # Add segment info to summary
            segment_info = {
                "segment_name": segment_name,
                "frames_count": frames_in_segment,
                "metadata": segment_metadata
            }
            dataset_summary["segments"].append(segment_info)
        
        # Update total frames in summary
        dataset_summary["total_frames"] = total_frames_copied
        
        # Save dataset summary
        summary_path = self.unified_dataset_dir / "dataset_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(dataset_summary, f, indent=2)
        
        # Create a simple text file with frame list for easy reference
        frame_list_path = self.unified_dataset_dir / "frame_list.txt"
        frame_files = list(dataset_images_dir.glob("*.jpg"))
        frame_files.sort()
        
        with open(frame_list_path, 'w') as f:
            f.write(f"Unified Video Dataset\n")
            f.write(f"Generated by Video Segment Annotator\n")
            f.write(f"Total Frames: {len(frame_files)}\n")
            f.write(f"Total Segments: {len(segment_folders)}\n")
            f.write(f"Created: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"\nFrame Files:\n")
            f.write("=" * 50 + "\n")
            for frame_file in frame_files:
                f.write(f"{frame_file.name}\n")
        
        messagebox.showinfo("Success", 
            f"Unified dataset created successfully!\n\n"
            f"📊 Total frames: {total_frames_copied}\n"
            f"📁 Total segments: {len(segment_folders)}\n"
            f"💾 Location: unified_dataset/\n\n"
            f"Images: unified_dataset/images/\n"
            f"Metadata: unified_dataset/metadata/\n"
            f"Summary: unified_dataset/dataset_summary.json")
        
        self.status_var.set(f"✅ Created unified dataset with {total_frames_copied} frames from {len(segment_folders)} segments")
    
    def open_output_folder(self):
        """Open the output folder in file explorer"""
        import subprocess
        import platform
        
        if platform.system() == "Windows":
            subprocess.run(["explorer", str(self.project_dir)])
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", str(self.project_dir)])
        else:  # Linux
            subprocess.run(["xdg-open", str(self.project_dir)])
    
    def show_dataset_stats(self):
        """Show dataset statistics"""
        stats_text = self.get_dataset_statistics()
        
        # Create a new window for stats
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Dataset Statistics")
        stats_window.geometry("600x400")
        
        # Text widget with scrollbar
        text_frame = ttk.Frame(stats_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget.insert(tk.END, stats_text)
        text_widget.config(state=tk.DISABLED)
        
    def get_dataset_statistics(self):
        """Get comprehensive dataset statistics"""
        stats = []
        stats.append("📊 VIDEO SEGMENT ANNOTATOR - DATASET STATISTICS\n")
        stats.append("=" * 60 + "\n\n")
        
        # Check for segments
        segments_frames_dir = self.segments_dir / "frames"
        segments_videos_dir = self.segments_dir / "videos"
        
        if segments_frames_dir.exists():
            segment_folders = [f for f in segments_frames_dir.iterdir() if f.is_dir()]
            stats.append(f"📁 Extracted Segments: {len(segment_folders)}\n")
            
            total_frames = 0
            for folder in segment_folders:
                frame_count = len(list(folder.glob("frame_*.jpg")))
                total_frames += frame_count
            
            stats.append(f"🖼️  Total Extracted Frames: {total_frames}\n")
        else:
            stats.append("📁 Extracted Segments: 0\n")
            stats.append("🖼️  Total Extracted Frames: 0\n")
        
        if segments_videos_dir.exists():
            video_files = list(segments_videos_dir.glob("*.mp4"))
            stats.append(f"🎥 Segment Videos: {len(video_files)}\n")
        else:
            stats.append("🎥 Segment Videos: 0\n")
        
        # Check for unified dataset
        if self.unified_dataset_dir.exists():
            dataset_images_dir = self.unified_dataset_dir / "images"
            summary_file = self.unified_dataset_dir / "dataset_summary.json"
            
            if dataset_images_dir.exists():
                unified_frames = list(dataset_images_dir.glob("*.jpg"))
                stats.append(f"📊 Unified Dataset Frames: {len(unified_frames)}\n")
            else:
                stats.append("📊 Unified Dataset Frames: 0\n")
                
            if summary_file.exists():
                try:
                    with open(summary_file, 'r') as f:
                        summary = json.load(f)
                    stats.append(f"📅 Dataset Created: {summary.get('creation_timestamp', 'Unknown')}\n")
                except:
                    pass
        else:
            stats.append("📊 Unified Dataset: Not created\n")
        
        stats.append(f"\n📂 Project Directory: {self.project_dir}\n")
        stats.append(f"🎬 Videos Directory: {self.videos_dir}\n")
        stats.append(f"📤 Segments Directory: {self.segments_dir}\n")
        stats.append(f"📊 Dataset Directory: {self.unified_dataset_dir}\n")
        
        # Input videos stats
        video_count = len(self.video_files)
        stats.append(f"\n🎬 Input Videos Available: {video_count}\n")
        
        if video_count > 0:
            stats.append("\nInput Video Files:\n")
            for i, video_path in enumerate(self.video_files):
                stats.append(f"  {i+1}. {video_path.name}\n")
        
        return "".join(stats)
        
    def run(self):
        """Run the application"""
        self.root.mainloop()
        
        # Cleanup
        if self.cap:
            self.cap.release()

def main():
    """Main function to run the Video Segment Annotator"""
    print("🎬 Starting Video Segment Annotator...")
    print("📁 Make sure to place your video files in the 'videos' folder")
    
    app = VideoSegmentAnnotator()
    app.run()

if __name__ == "__main__":
    main()
