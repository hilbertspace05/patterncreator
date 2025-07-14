from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import random
import math

def non_overlapping_circle_packed_image(image_path, output_path, min_radius=3, max_radius=25, density_factor=1.5, max_attempts=50):
    """
    Circle packing with no overlaps and varied circle sizes
    """
    print(f"Starting non-overlapping circle packing transformation...")
    
    img = Image.open(image_path).convert('RGB')
    width, height = img.size
    canvas = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    img_np = np.array(img)
    
    print(f"Image dimensions: {width}x{height}")
    
    # Store placed circles for collision detection
    placed_circles = []
    
    def get_avg_color(x, y, r):
        x_min = max(0, x - r)
        x_max = min(width, x + r)
        y_min = max(0, y - r)
        y_max = min(height, y + r)
        
        region = img_np[y_min:y_max, x_min:x_max]
        if region.size == 0:
            return (128, 128, 128)
        
        avg_color = np.mean(region.reshape(-1, 3), axis=0)
        return tuple(avg_color.astype(int))
    
    def darken_color(color, factor=0.3):
        """Darken a color for outline effect"""
        return tuple(max(0, int(c * (1 - factor))) for c in color)
    
    def circles_overlap(x1, y1, r1, x2, y2, r2, buffer=2):
        """Check if two circles overlap with a small buffer"""
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        return distance < (r1 + r2 + buffer)
    
    def can_place_circle(x, y, r):
        """Check if a circle can be placed without overlapping existing circles"""
        # Check boundaries
        if x - r < 0 or x + r > width or y - r < 0 or y + r > height:
            return False
        
        # Check overlap with existing circles
        for existing_x, existing_y, existing_r in placed_circles:
            if circles_overlap(x, y, r, existing_x, existing_y, existing_r):
                return False
        
        return True
    
    def get_varied_radius():
        """Generate varied circle sizes with bias toward medium sizes"""
        # Create size distribution: more medium circles, fewer very large/small
        size_weights = [0.2, 0.3, 0.3, 0.15, 0.05]  # small to large
        size_ranges = [
            (min_radius, min_radius + 3),
            (min_radius + 3, min_radius + 8),
            (min_radius + 8, min_radius + 13),
            (min_radius + 13, min_radius + 18),
            (min_radius + 18, max_radius)
        ]
        
        chosen_range = random.choices(size_ranges, weights=size_weights)[0]
        return random.randint(chosen_range[0], min(chosen_range[1], max_radius))
    
    print("\nPhase 1: Placing non-overlapping circles with size variation...")
    
    circles_placed = 0
    total_attempts = 0
    
    # Calculate target number of circles
    avg_circle_area = math.pi * ((min_radius + max_radius) / 2) ** 2
    image_area = width * height
    target_circles = int((image_area / avg_circle_area) * density_factor)
    
    # Try to place circles until we reach target or max attempts
    while circles_placed < target_circles and total_attempts < target_circles * max_attempts:
        # Generate random position and varied size
        r = get_varied_radius()
        x = random.randint(r, width - r)
        y = random.randint(r, height - r)
        
        if can_place_circle(x, y, r):
            # Place the circle
            color = get_avg_color(x, y, r)
            outline_color = darken_color(color, 0.4)
            outline_width = max(1, r // 5)
            
            draw.ellipse((x - r, y - r, x + r, y + r),
                        fill=color, outline=outline_color, width=outline_width)
            
            # Store circle info for future collision detection
            placed_circles.append((x, y, r))
            circles_placed += 1
            
            if circles_placed % 50 == 0:
                print(f" Circles placed: {circles_placed}/{target_circles}")
        
        total_attempts += 1
        
        # Progress update
        if total_attempts % 1000 == 0:
            success_rate = (circles_placed / total_attempts) * 100
            print(f" Attempts: {total_attempts}, Success rate: {success_rate:.1f}%")
    
    print("\nPhase 2: Filling gaps with smaller circles...")
    
    # Fill remaining space with smaller circles
    gap_fill_attempts = target_circles // 2
    for i in range(gap_fill_attempts):
        # Use smaller circles for gap filling
        r = random.randint(min_radius, min_radius + 5)
        x = random.randint(r, width - r)
        y = random.randint(r, height - r)
        
        if can_place_circle(x, y, r):
            color = get_avg_color(x, y, r)
            outline_color = darken_color(color, 0.3)
            outline_width = max(1, r // 6)
            
            draw.ellipse((x - r, y - r, x + r, y + r),
                        fill=color, outline=outline_color, width=outline_width)
            
            placed_circles.append((x, y, r))
            circles_placed += 1
    
    # Calculate size distribution statistics
    sizes = [r for _, _, r in placed_circles]
    size_stats = {
        'min': min(sizes),
        'max': max(sizes),
        'avg': sum(sizes) / len(sizes),
        'total_circles': len(sizes)
    }
    
    canvas.save(output_path)
    
    print(f"\n✅ Non-overlapping circle packing completed!")
    print(f"📁 Output saved to: {output_path}")
    print(f"🎯 Total circles placed: {circles_placed}")
    print(f"📊 Size distribution:")
    print(f"   - Smallest circle: {size_stats['min']} pixels")
    print(f"   - Largest circle: {size_stats['max']} pixels")
    print(f"   - Average size: {size_stats['avg']:.1f} pixels")
    
    return output_path

# Usage
non_overlapping_circle_packed_image('imagem2.jpg', 'non_overlapping_circles.jpg')
