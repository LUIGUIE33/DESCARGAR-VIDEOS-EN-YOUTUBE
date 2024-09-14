import streamlit as st
import yt_dlp
import os
from queue import Queue
from threading import Thread

def download_video(url, output_path):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': output_path,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        title = info['title']
        ydl.download([url])
    return title

def worker(queue, output_folder, completed_videos):
    while True:
        url = queue.get()
        if url is None:
            break
        try:
            output_path = os.path.join(output_folder, '%(title)s.%(ext)s')
            title = download_video(url, output_path)
            completed_videos.append(f"✅ {title}")
            st.success(f'Video descargado exitosamente: {title}')
        except Exception as e:
            completed_videos.append(f"❌ Error: {url}")
            st.error(f'Error al descargar el video {url}: {str(e)}')
        finally:
            queue.task_done()

st.title('Descarga videos de YouTube')
st.subheader('by: LUIS ESC🦖')
st.caption('Este programa descarga videos en la máxima calidad disponible')

urls = st.text_area('Ingresa las URLs de los videos de YouTube (una por línea):')
output_folder = st.text_input('Ingresa la carpeta de salida:', 'descargas')
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

if st.button('Descargar'):
    if urls:
        url_list = urls.split('\n')
        url_list = [url.strip() for url in url_list if url.strip()]
        
        if url_list:
            queue = Queue()
            completed_videos = []
            for url in url_list:
                queue.put(url)
            
            num_worker_threads = 3
            threads = []
            for _ in range(num_worker_threads):
                t = Thread(target=worker, args=(queue, output_folder, completed_videos))
                t.start()
                threads.append(t)
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            total_videos = len(url_list)
            processed_videos = 0
            
            while not queue.empty():
                processed_videos = total_videos - queue.qsize()
                progress = processed_videos / total_videos
                progress_bar.progress(progress)
                status_text.text(f'Descargando... {processed_videos}/{total_videos} videos procesados')
                
            queue.join()
            
            for _ in range(num_worker_threads):
                queue.put(None)
            for t in threads:
                t.join()
            
            progress_bar.progress(1.0)
            status_text.text(f'Descarga completada: {total_videos}/{total_videos} videos')
            st.balloons()

            st.subheader("Videos descargados:")
            for video in completed_videos:
                st.write(video)
        else:
            st.warning('Por favor, ingrese al menos una URL válida.')
    else:
        st.warning('Por favor, ingrese al menos una URL válida.')