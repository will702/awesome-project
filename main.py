import cv2
import dlib
from imutils import face_utils
from flask import Flask,request,jsonify
from werkzeug.utils import secure_filename

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

(left_Start, left_End) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
# points for left eye and right eye
(right_Start, right_End) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]


def get_image_with_landmarks(file_path: str):
    flag = 0

    try:
        image = cv2.imread(file_path, 1)

        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)

        dlib_faces = detector(gray, 0)



    except Exception:
        return {'error': 'Error while reading the image'}

    for face in dlib_faces:
        eyes = []  #
        (x, y, w, h) = face_utils.rect_to_bb(face)
        cv2.rectangle(img_rgb, (x, y), (x + w, y + h), (255, 0, 0), 1)  # draws blue box over face

        shape = predictor(gray, face)
        shape = face_utils.shape_to_np(shape)

        leftEye = shape[left_Start:left_End]
        # indexes for left eye key points

        rightEye = shape[right_Start:right_End]

        eyes.append(leftEye)  # wrap in a list
        eyes.append(rightEye)

        for index, eye in enumerate(eyes):
            flag += 1
            left_side_eye = eye[0]  # left edge of eye
            right_side_eye = eye[3]  # right edge of eye
            top_side_eye = eye[1]  # top side of eye
            bottom_side_eye = eye[4]  # bottom side of eye

            # calculate height and width of dlib eye keypoints
            eye_width = right_side_eye[0] - left_side_eye[0]
            eye_height = bottom_side_eye[1] - top_side_eye[1]

            # create bounding box with buffer around keypoints
            eye_x1 = int(left_side_eye[0] - 0 * eye_width)
            eye_x2 = int(right_side_eye[0] + 0 * eye_width)

            eye_y1 = int(top_side_eye[1] - 1 * eye_height)
            eye_y2 = int(bottom_side_eye[1] + 0.75 * eye_height)

            # draw bounding box around eye roi

            # cv2.rectangle(img_rgb,(eye_x1, eye_y1), (eye_x2, eye_y2),(0,255,0),2)

            roi_eye = img_rgb[eye_y1:eye_y2, eye_x1:eye_x2]  # desired EYE Region(RGB)
            if flag == 1:
                break

    x = roi_eye.shape
    row = x[0]
    col = x[1]
    # this is the main part,
    # where you pick RGB values from the area just below pupil
    array1 = roi_eye[row // 2:(row // 2) + 1, int((col // 3) + 3):int((col // 3)) + 6]

    array1 = array1[0][2]

    array1 = tuple(array1)  # store it in tuple and pass this tuple to "find_color" Funtion



    return str(array1)

app = Flask(__name__)
@app.route('/',methods=["GET","POST"])
def index():
    if request.method == "POST":
        file = request.files.get("file")
        if file is None or file.filename == "":
            return jsonify({"error": "no file"})
        try:

            f = request.files['file']
            f.save(secure_filename(f.filename))
            return jsonify({'results':get_image_with_landmarks(f.filename)})


        except Exception as e:
            return jsonify({"error": str(e)})

    return "OK"
if __name__ == '__main__':
    app.run(debug=True)
