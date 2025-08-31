import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.table import Table
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

def create_timetable_image(csv_file_path, output_image_path="timetable.png"):
    """
    Create a user-friendly timetable image from CSV with merged cells
    """
    # Read the CSV file
    df = pd.read_csv(csv_file_path)
    
    # Clean column names (remove line breaks)
    df.columns = [col.replace('\n', ' ') for col in df.columns]
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(16, 12))
    ax.axis('off')
    
    # Define colors
    header_color = '#2E86AB'
    time_color = '#A23B72'
    cell_colors = ['#F18F01', '#C73E1D', '#592E83', '#1B998B', '#A4243B']
    empty_color = '#F5F5F5'
    text_color = '#FFFFFF'
    
    # Calculate cell dimensions
    rows, cols = df.shape
    cell_width = 0.12
    cell_height = 0.06
    
    # Track merged cells to avoid drawing duplicates
    merged_cells = set()
    
    # Function to determine if cells should be merged
    def should_merge_cells(col_idx, start_row, end_row):
        if col_idx == 0:  # Don't merge time column
            return False
        
        base_value = df.iloc[start_row, col_idx]
        if pd.isna(base_value) or base_value == '':
            return False
            
        for row in range(start_row + 1, end_row + 1):
            if row >= len(df):
                break
            current_value = df.iloc[row, col_idx]
            if current_value != base_value:
                return False
        return True
    
    # Find merge groups for each column
    merge_groups = {}
    for col_idx in range(1, cols):  # Skip time column
        merge_groups[col_idx] = []
        start_row = 0
        
        while start_row < rows:
            end_row = start_row
            base_value = df.iloc[start_row, col_idx]
            
            # Find consecutive identical cells
            while (end_row + 1 < rows and 
                   df.iloc[end_row + 1, col_idx] == base_value and 
                   not pd.isna(base_value) and base_value != ''):
                end_row += 1
            
            if end_row > start_row:  # Found a merge group
                merge_groups[col_idx].append((start_row, end_row, base_value))
            
            start_row = end_row + 1
    
    # Draw header
    for col_idx, col_name in enumerate(df.columns):
        x = col_idx * cell_width
        y = 1 - cell_height
        
        # Header rectangle
        rect = patches.Rectangle((x, y), cell_width, cell_height, 
                               linewidth=1, edgecolor='white', 
                               facecolor=header_color)
        ax.add_patch(rect)
        
        # Header text
        ax.text(x + cell_width/2, y + cell_height/2, col_name, 
               ha='center', va='center', fontsize=10, 
               color=text_color, weight='bold', wrap=True)
    
    # Draw data cells
    for row_idx in range(rows):
        for col_idx in range(cols):
            if (row_idx, col_idx) in merged_cells:
                continue
                
            x = col_idx * cell_width
            y = 1 - (row_idx + 2) * cell_height
            
            cell_value = df.iloc[row_idx, col_idx]
            
            # Check if this cell is part of a merge group
            merge_height = cell_height
            is_merged = False
            
            if col_idx in merge_groups:
                for start_row, end_row, merge_value in merge_groups[col_idx]:
                    if start_row <= row_idx <= end_row and cell_value == merge_value:
                        if row_idx == start_row:  # Only draw for the first cell in merge group
                            merge_height = cell_height * (end_row - start_row + 1)
                            # Mark other cells as merged
                            for r in range(start_row + 1, end_row + 1):
                                merged_cells.add((r, col_idx))
                        else:
                            is_merged = True
                        break
            
            if is_merged:
                continue
            
            # Choose cell color
            if col_idx == 0:  # Time column
                color = time_color
            elif pd.isna(cell_value) or cell_value == '':
                color = empty_color
                text_color_cell = '#333333'
            else:
                color = cell_colors[col_idx % len(cell_colors)]
                text_color_cell = text_color
            
            # Draw cell rectangle
            rect = patches.Rectangle((x, y), cell_width, merge_height, 
                                   linewidth=1, edgecolor='white', 
                                   facecolor=color)
            ax.add_patch(rect)
            
            # Draw cell text
            if not (pd.isna(cell_value) or cell_value == ''):
                # Special handling for time column (first column)
                if col_idx == 0:
                    # Convert single time to time interval
                    time_text = str(cell_value).strip()
                    if ':' in time_text and '-' not in time_text:
                        # Parse time and add 1 hour
                        try:
                            from datetime import datetime, timedelta
                            # Handle different time formats
                            if 'AM' in time_text.upper() or 'PM' in time_text.upper():
                                # 12-hour format
                                time_obj = datetime.strptime(time_text.upper(), '%I:%M%p')
                            else:
                                # 24-hour format
                                time_obj = datetime.strptime(time_text, '%H:%M')
                            
                            # Add 1 hour
                            end_time = time_obj + timedelta(hours=1)
                            
                            # Format back to original format
                            if 'AM' in time_text.upper() or 'PM' in time_text.upper():
                                start_formatted = time_obj.strftime('%I:%M%p')
                                end_formatted = end_time.strftime('%I:%M%p')
                            else:
                                start_formatted = time_obj.strftime('%H:%M')
                                end_formatted = end_time.strftime('%H:%M')
                            
                            time_text = f"{start_formatted}-{end_formatted}"
                        except:
                            # If parsing fails, keep original text
                            pass
                    
                    all_lines = [(time_text, font_cell)]
                    
                elif '|' in str(cell_value):
                    parts = str(cell_value).split('|')
                    if len(parts) >= 4:
                        # Parse: MODULE_CODE - GROUP|Module Name|Type|Time|Location
                        module_code = parts[0].strip()  # e.g., "INF 1001 - ALL"
                        module_name = parts[1].strip()  # e.g., "Introduction to Computing"
                        lesson_type = parts[2].strip()  # e.g., "Lecture"
                        lesson_time = parts[3].strip()  # e.g., "9:00AM - 11:00AM"
                        location = parts[4].strip() if len(parts) > 4 else ""  # e.g., "Online"
                        
                        # Prepare text lines with wrapping
                        all_lines = []
                        
                        # Module code (no wrapping needed, usually short)
                        all_lines.append((module_code, font_cell))
                        
                        # Module name with wrapping
                        wrapped_name = wrap_text(module_name, font_module, cell_width - 30)
                        for line in wrapped_name:
                            all_lines.append((line, font_module))
                        
                        # Lesson type and time
                        lesson_info = f"{lesson_type}"
                        wrapped_info = wrap_text(lesson_info, font_small, cell_width - 30)
                        for line in wrapped_info:
                            all_lines.append((line, font_small))
                        
                        # Location if available
                        if location:
                            wrapped_location = wrap_text(location, font_small, cell_width - 30)
                            for line in wrapped_location:
                                all_lines.append((line, font_small))
                    else:
                        # Fallback for other formats
                        text_lines = str(cell_value).split('|')
                        all_lines = [(line, font_cell) for line in text_lines]
                else:
                    all_lines = [(str(cell_value), font_cell)]
                
                # Calculate text positioning
                line_height = 40  # was 20
                total_text_height = len(all_lines) * line_height
                start_y = y + (cell_height_merged - total_text_height) // 2
                
                for i, (line, font) in enumerate(all_lines):
                    if line.strip():
                        text_bbox = draw.textbbox((0, 0), line, font=font)
                        text_width = text_bbox[2] - text_bbox[0]
                        
                        text_x = x + (cell_width - text_width) // 2
                        text_y = start_y + i * line_height
                        
                        draw.text((text_x, text_y), line, fill=text_color, font=font)
    
    # Set axis limits and aspect
    ax.set_xlim(0, cols * cell_width)
    ax.set_ylim(1 - (rows + 2) * cell_height, 1)
    ax.set_aspect('equal')
    
    # Add title
    plt.suptitle('Weekly Timetable', fontsize=16, fontweight='bold', y=0.95)
    
    # Save the image
    plt.tight_layout()
    plt.savefig(output_image_path, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    
    return output_image_path

def create_simple_timetable_image(csv_file_path, output_image_path="timetable_simple.png"):
    """
    Create a simpler timetable image using PIL for better text handling
    """
    # Read the CSV file
    df1 = pd.read_csv(csv_file_path)
    df = df1.iloc[:-3]
    
    # Clean column names
    df.columns = [col.replace('\n', ' ') for col in df.columns]
    
    # Filter out Saturday and Sunday columns
    columns_to_keep = []
    for col in df.columns:
        col_lower = col.lower()
        if not any(day in col_lower for day in ['saturday', 'sunday', 'sat|', 'sun|']):
            columns_to_keep.append(col)
    
    df = df[columns_to_keep]
    print(f"Filtered columns: {list(df.columns)}")
    
    # Image dimensions - increased further for much larger fonts
    cell_width = 500
    cell_height = 250
    header_height = 120
    
    img_width = len(df.columns) * cell_width
    img_height = header_height + len(df) * cell_height
    
    # Create image
    img = Image.new('RGB', (img_width, img_height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Try to load fonts with doubled sizes
    try:
        font_header = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 34)  # was 22
        font_module = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)  # was 16
        font_cell = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)  # was 14
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)  # was 12
    except:
        font_header = ImageFont.load_default()
        font_module = ImageFont.load_default()
        font_cell = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Colors
    colors = {
        'header': '#2E86AB',
        'time': '#A23B72', 
        'course': ['#F18F01', '#C73E1D', '#592E83', '#1B998B', '#A4243B'],
        'empty': '#F5F5F5',
        'text_white': '#FFFFFF',
        'text_dark': '#333333'
    }
    
    def wrap_text(text, font, max_width):
        """Wrap text to fit within max_width"""
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            text_bbox = draw.textbbox((0, 0), test_line, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            
            if text_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    # Single word is too long, truncate it
                    lines.append(word[:15] + "..." if len(word) > 15 else word)
                    current_line = ""
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    # Draw headers
    for col_idx, col_name in enumerate(df.columns):
        x = col_idx * cell_width
        y = 0
        
        # Header background
        draw.rectangle([x, y, x + cell_width, y + header_height], 
                      fill=colors['header'], outline='white', width=3)
        
        # Header text with wrapping
        wrapped_header = wrap_text(col_name, font_header, cell_width - 30)
        line_height = 50  # was 25
        total_height = len(wrapped_header) * line_height
        start_y = y + (header_height - total_height) // 2
        
        for i, line in enumerate(wrapped_header):
            text_bbox = draw.textbbox((0, 0), line, font=font_header)
            text_width = text_bbox[2] - text_bbox[0]
            text_x = x + (cell_width - text_width) // 2
            text_y = start_y + i * line_height
            draw.text((text_x, text_y), line, fill=colors['text_white'], font=font_header)
    
    # Track merged cells
    drawn_cells = set()
    
    # Draw data cells with merging
    for row_idx in range(len(df)):
        for col_idx in range(len(df.columns)):
            if (row_idx, col_idx) in drawn_cells:
                continue
                
            cell_value = df.iloc[row_idx, col_idx]
            x = col_idx * cell_width
            y = header_height + row_idx * cell_height
            
            # Check for vertical merging
            merge_count = 1
            if col_idx > 0 and not (pd.isna(cell_value) or cell_value == ''):
                for check_row in range(row_idx + 1, len(df)):
                    if df.iloc[check_row, col_idx] == cell_value:
                        merge_count += 1
                        drawn_cells.add((check_row, col_idx))
                    else:
                        break
            
            # Choose colors
            if col_idx == 0:  # Time column
                bg_color = colors['time']
                text_color = colors['text_white']
            elif pd.isna(cell_value) or cell_value == '':
                bg_color = colors['empty']
                text_color = colors['text_dark']
            else:
                bg_color = colors['course'][col_idx % len(colors['course'])]
                text_color = colors['text_white']
            
            # Draw cell background
            cell_height_merged = cell_height * merge_count
            draw.rectangle([x, y, x + cell_width, y + cell_height_merged], 
                          fill=bg_color, outline='white', width=3)
            
            # Draw cell text
            if not (pd.isna(cell_value) or cell_value == ''):
                if '|' in str(cell_value):
                    parts = str(cell_value).split('|')
                    if len(parts) >= 4:
                        # Parse: MODULE_CODE - GROUP|Module Name|Type|Time|Location
                        module_code = parts[0].strip()  # e.g., "INF 1001 - ALL"
                        module_name = parts[1].strip()  # e.g., "Introduction to Computing"
                        lesson_type = parts[2].strip()  # e.g., "Lecture"
                        lesson_time = parts[3].strip()  # e.g., "9:00AM - 11:00AM"
                        location = parts[4].strip() if len(parts) > 4 else ""  # e.g., "Online"
                        
                        # Prepare text lines with wrapping
                        all_lines = []
                        
                        # Module code (no wrapping needed, usually short)
                        all_lines.append((module_code, font_cell))
                        
                        # Module name with wrapping
                        wrapped_name = wrap_text(module_name, font_module, cell_width - 30)
                        for line in wrapped_name:
                            all_lines.append((line, font_module))
                        
                        # Lesson type and time
                        lesson_info = f"{lesson_type}"
                        wrapped_info = wrap_text(lesson_info, font_small, cell_width - 30)
                        for line in wrapped_info:
                            all_lines.append((line, font_small))
                        
                        # Location if available
                        if location:
                            wrapped_location = wrap_text(location, font_small, cell_width - 30)
                            for line in wrapped_location:
                                all_lines.append((line, font_small))
                    else:
                        # Fallback for other formats
                        text_lines = str(cell_value).split('|')
                        all_lines = [(line, font_cell) for line in text_lines]
                else:
                    all_lines = [(str(cell_value), font_cell)]
                
                # Calculate text positioning
                line_height = 40  # was 20
                total_text_height = len(all_lines) * line_height
                start_y = y + (cell_height_merged - total_text_height) // 2
                
                for i, (line, font) in enumerate(all_lines):
                    if line.strip():
                        text_bbox = draw.textbbox((0, 0), line, font=font)
                        text_width = text_bbox[2] - text_bbox[0]
                        
                        text_x = x + (cell_width - text_width) // 2
                        text_y = start_y + i * line_height
                        
                        draw.text((text_x, text_y), line, fill=text_color, font=font)
    
    # Save image
    img.save(output_image_path, 'PNG', quality=95)
    return output_image_path

def main():
    """
    Main function to run the timetable image generator as a standalone script
    """
    import sys
    
    # Default file paths
    csv_file = "weekly_schedule_timetable.csv"
    output_file = "timetable_image.png"
    
    # Check if custom file paths are provided as command line arguments
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    # Check if CSV file exists
    if not os.path.exists(csv_file):
        print(f"Error: CSV file '{csv_file}' not found.")
        print("Usage: python timetable_image_generator.py [csv_file] [output_image]")
        return
    
    try:
        print(f"Generating timetable image from '{csv_file}'...")
        result_path = create_simple_timetable_image(csv_file, output_file)
        print(f"Timetable image successfully saved to: {result_path}")
    except Exception as e:
        print(f"Error generating timetable image: {e}")

if __name__ == "__main__":
    main()