# Video Segment Annotator

A powerful and user-friendly GUI tool for video annotation, segmentation, and dataset creation. Perfect for machine learning practitioners, researchers, and data scientists who need to create frame-based datasets from video content.

## 🎯 Features

- **Interactive Video Player**: Play, pause, seek, and navigate through videos with precision
- **Segment Annotation**: Mark start and end points of interesting segments in videos
- **Batch Processing**: Process multiple videos sequentially 
- **Automatic Segmentation**: Export marked segments as individual video files
- **Frame Extraction**: Automatically extract frames from each segment with metadata
- **Unified Dataset Creation**: Combine all extracted frames into a single organized dataset
- **Metadata Preservation**: Complete tracking of original video source, timing, and properties
- **Cross-Platform**: Works on Windows, macOS, and Linux

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/video-segment-annotator.git
cd video-segment-annotator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python video_annotator.py
```

## 📖 Usage

1. **Setup Videos**: Place your video files in the `videos/` folder
2. **Launch Tool**: Run `python video_annotator.py`
3. **Annotate**: 
   - Use Previous/Next to navigate between videos
   - Click "Mark Start" at the beginning of interesting segments
   - Click "Mark End" at the end of segments
   - Review your segments in the list
4. **Export**: Click "Export Segments & Extract Frames" to process marked segments
5. **Create Dataset**: Use "Create Unified Dataset" to combine all frames

## 📁 Project Structure

```
video-segment-annotator/
├── video_annotator.py          # Main application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── videos/                     # Place your input videos here
├── segments/                   # Generated segment videos
│   ├── frames/                 # Extracted frames from segments
│   └── videos/                 # Individual segment video files
└── unified_dataset/            # Final combined dataset
    ├── images/                 # All frames combined
    ├── metadata/               # Segment metadata files
    └── dataset_summary.json    # Complete dataset information
```

## 🎮 Controls

### Video Navigation
- **Previous Video / Next Video**: Switch between videos in the folder
- **Play/Pause (▶/⏸)**: Control video playback
- **Seek Backward (◀◀)**: Jump back 5 seconds
- **Seek Forward (▶▶)**: Jump forward 5 seconds
- **Progress Bar**: Click to jump to specific time

### Annotation
- **Mark Start**: Set beginning of segment at current time
- **Mark End**: Set end of segment at current time
- **Clear Last**: Remove the most recently added segment
- **Clear All**: Remove all segments for current video

### Export
- **Export Segments & Extract Frames**: Process current video's segments
- **Create Unified Dataset**: Combine all extracted frames from all videos

## 📊 Output Format

### Segment Videos
Individual video files for each marked segment:
```
segments/videos/
├── video1_segment_1.mp4
├── video1_segment_2.mp4
└── video2_segment_1.mp4
```

### Frame Extraction
Organized folders with frames and metadata:
```
segments/frames/
├── video1_segment_1/
│   ├── frame_0001.jpg
│   ├── frame_0002.jpg
│   └── metadata.json
└── video1_segment_2/
    ├── frame_0001.jpg
    └── metadata.json
```

### Unified Dataset
Combined dataset ready for machine learning:
```
unified_dataset/
├── images/                    # All frames with unique names
│   ├── video1_segment_1_frame_0001.jpg
│   ├── video1_segment_1_frame_0002.jpg
│   └── video2_segment_1_frame_0001.jpg
├── metadata/                  # Original segment metadata
└── dataset_summary.json       # Complete dataset statistics
```

## 🔧 Supported Formats

- **Input Videos**: MP4, AVI, MOV
- **Output Videos**: MP4 (configurable)
- **Output Images**: JPG (configurable)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏷️ Tags

`video-annotation` `machine-learning` `dataset-creation` `computer-vision` `data-preprocessing` `video-processing` `frame-extraction` `gui-application` `python` `opencv` `tkinter`

## 🌟 Use Cases

- **Sports Analysis**: Extract action sequences from game footage
- **Security**: Annotate incidents in surveillance videos  
- **Medical**: Segment procedures in medical videos
- **Education**: Create clips from lecture recordings
- **Research**: Build datasets for computer vision models
- **Content Creation**: Extract highlights from long-form content

## 📈 Performance

- Handles videos of any length and resolution
- Efficient memory usage with frame-by-frame processing
- Fast export with OpenCV optimization
- Batch processing capability for multiple videos

---

⭐ **Star this repository if it helps your project!**
