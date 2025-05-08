import cv2

# Global variables
rectangles = {}
start_x, start_y = -1, -1
drawing = False
max_rects = 10  # Define 10 zones
frame_copy = None
rect_count = 1  # Start numeric keys from 1

def draw_rectangle(event, x, y, flags, param):
    """ Callback function to draw and store rectangles """
    global start_x, start_y, drawing, rectangles, frame_copy, rect_count

    if event == cv2.EVENT_LBUTTONDOWN:  # Start drawing
        drawing = True
        start_x, start_y = x, y

    elif event == cv2.EVENT_MOUSEMOVE:  # Show live rectangle
        if drawing:
            temp_frame = frame_copy.copy()
            cv2.rectangle(temp_frame, (start_x, start_y), (x, y), (0, 255, 0), 2)
            cv2.imshow("Select Areas", temp_frame)

    elif event == cv2.EVENT_LBUTTONUP:  # Finish drawing
        drawing = False
        end_x, end_y = x, y

        # Ensure (x1, y1) is the top-left and (x2, y2) is the bottom-right
        x1, x2 = min(start_x, end_x), max(start_x, end_x)
        y1, y2 = min(start_y, end_y), max(start_y, end_y)

        if rect_count <= max_rects:
            rectangles[rect_count] = (x1, y1, x2, y2)  # Store as tuples
            rect_count += 1
            cv2.rectangle(frame_copy, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.imshow("Select Areas", frame_copy)

# Load video
video_path = "input_videos\\56_2025NECMP2.mp4"  # Change this to your video file
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

# Read the first frame
ret, frame = cap.read()
cap.release()  # Close the video since we only need the first frame

if not ret:
    print("Error: Could not read first frame.")
    exit()

frame_copy = frame.copy()

cv2.imshow("Select Areas", frame_copy)
cv2.setMouseCallback("Select Areas", draw_rectangle)

# Wait until 10 rectangles are selected
while len(rectangles) < max_rects:
    cv2.waitKey(1)

cv2.destroyAllWindows()

# Export to text file in the exact format
output_filename = "selected_zones.txt"
with open(output_filename, "w") as f:
    f.write("{\n")
    for i, coords in rectangles.items():
        f.write(f"    {i}: {coords},\n")
    f.write("}\n")

print(f"Selected zones saved to {output_filename}!")