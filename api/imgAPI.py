import os
import uuid
from flask import Blueprint, request, jsonify
from firebase_admin import firestore, storage

db = firestore.client()
user_Ref = db.collection('imagenes')
bucket = storage.bucket()

imgAPI = Blueprint('imgAPI', __name__)

@imgAPI.route('/add', methods = ['POST'])
def create():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No se proporcionó un archivo'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No se proporcionó un archivo válido'}), 400

        # Generar un nombre único para el archivo
        file_name = f"{str(uuid.uuid4())}.{file.filename.split('.')[-1]}"

        # Subir la imagen a Firebase Storage
        blob = bucket.blob(file_name)
        blob.upload_from_string(file.read(), content_type=file.content_type)

        # Obtener la URL de la imagen cargada
        image_url = blob.public_url
        #print(storage.child(file_name).get_url(None))

        # Guardar la URL y el nombre de la imagen en Cloud Firestore
        document_data = {
            'image_url': image_url,
            'image_name': file_name,
            'id_foranea': int(request.form['id_foranea'])  # Asegúrate de ajustar esto según tus necesidades
        }

        id = uuid.uuid4()
        user_Ref.document(id.hex).set(document_data)

        return jsonify({'success': True, 'image_url': image_url, 'image_name': file_name}), 200

    except Exception as e:
        return jsonify({'error': f"Ocurrió un error: {str(e)}"}), 500

@imgAPI.route('/list')
def read():
    try:
        all_imgs = [doc.to_dict() for doc in user_Ref.stream()]
        return jsonify({'data': all_imgs}), 200
    except Exception as e:
        return jsonify({'error': f"Ocurrió un error: {str(e)}"}), 500

@imgAPI.route('/edit/<id_foranea>', methods=['PUT'])
def update(id_foranea):
    try:
        # Buscar la imagen por id_foranea
        query = user_Ref.where('id_foranea', '==', int(id_foranea)).limit(1)
        image_docs = list(query.stream())

        # Verificar si la imagen existe
        if not image_docs:
            return jsonify({'error': 'La imagen no existe'}), 404

        image_ref = image_docs[0]

        # Obtener el archivo de la solicitud
        file = request.files.get('file')

        # Verificar si se proporcionó un nuevo archivo
        if file:
            #Borrar anterior
            # Obtener el nombre de la imagen
            image_data = image_ref.to_dict()
            image_name = image_data.get('image_name')
            # Eliminar la imagen de Firebase Storage
            blob = bucket.blob(image_name)
            blob.delete()

            # Generar un nuevo nombre único para el archivo
            new_file_name = f"{str(uuid.uuid4())}.{file.filename.split('.')[-1]}"

            # Subir el nuevo archivo a Firebase Storage
            blob = bucket.blob(new_file_name)
            blob.upload_from_string(file.read(), content_type=file.content_type)

            # Obtener la URL del nuevo archivo
            new_image_url = blob.public_url

            # Actualizar los datos en Firestore
            image_ref.reference.update({
                'image_name': new_file_name,
                'image_url': new_image_url
            })

            return jsonify({'success': True, 'message': 'Imagen actualizada correctamente'}), 200
        else:
            return jsonify({'error': 'No se proporcionó un nuevo archivo para actualizar'}), 400

    except Exception as e:
        return jsonify({'error': f"Ocurrió un error: {str(e)}"}), 500


@imgAPI.route('/delete/<id_foranea>', methods=['DELETE'])
def delete(id_foranea):
    try:
        # Buscar la imagen por id_foranea
        query = user_Ref.where('id_foranea', '==', int(id_foranea)).limit(1)
        image_docs = list(query.stream())

        # Verificar si la imagen existe
        if not image_docs:
            return jsonify({'error': 'La imagen no existe'}), 404

        image_ref = image_docs[0]

        # Obtener el nombre de la imagen
        image_data = image_ref.to_dict()
        image_name = image_data.get('image_name')

        # Verificar si el nombre de la imagen existe
        if not image_name:
            return jsonify({'error': 'No se encontró el nombre de la imagen'}), 500

        # Eliminar la imagen de Firebase Storage
        blob = bucket.blob(image_name)
        blob.delete()

        # Eliminar la entrada de Firestore
        image_ref.reference.delete()

        return jsonify({'success': True, 'message': 'Imagen eliminada correctamente'}), 200

    except Exception as e:
        return jsonify({'error': f"Ocurrió un error: {str(e)}"}), 500

