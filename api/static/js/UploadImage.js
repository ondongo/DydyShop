console.clear();

(function () {
  'use strict';

  const preventDefaults = event => {
    event.preventDefault();
    event.stopPropagation();
  };

  const highlight = event =>
    event.target.classList.add('highlight');

  const unhighlight = event =>
    event.target.classList.remove('highlight');

  const getInputAndGalleryRefs = element => {
    const zone = element.closest('.upload_dropZone') || false;
    const gallery = zone.querySelector('.upload_gallery') || false;
    const input = zone.querySelector('input[type="file"]') || false;
    return { input: input, gallery: gallery };
  }

  const handleDrop = event => {
    const dataRefs = getInputAndGalleryRefs(event.target);
    dataRefs.files = event.dataTransfer.files;
    handleFiles(dataRefs);
  }

  const removeImage = (dataRefs, imgElement) => {
    if (!dataRefs.gallery) return;
    dataRefs.gallery.removeChild(imgElement.parentNode); // Remove the container div
    dataRefs.files = dataRefs.files.filter(file => file.name !== imgElement.alt);
  };

  const eventHandlers = zone => {
    const dataRefs = getInputAndGalleryRefs(zone);
    if (!dataRefs.input) return;

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(event => {
      zone.addEventListener(event, preventDefaults, false);
      document.body.addEventListener(event, preventDefaults, false);
    });

    ['dragenter', 'dragover'].forEach(event => {
      zone.addEventListener(event, highlight, false);
    });

    ['dragleave', 'drop'].forEach(event => {
      zone.addEventListener(event, unhighlight, false);
    });

    zone.addEventListener('drop', handleDrop, false);

    dataRefs.input.addEventListener('change', event => {
      dataRefs.files = event.target.files;
      handleFiles(dataRefs);
    }, false);
  }

  const dropZones = document.querySelectorAll('.upload_dropZone');
  for (const zone of dropZones) {
    eventHandlers(zone);
  }

  const isImageFile = file =>
    ['image/jpeg', 'image/png', 'image/svg+xml'].includes(file.type);

  function previewFiles(dataRefs) {
    if (!dataRefs.gallery) return;

    for (const file of dataRefs.files) {
      let reader = new FileReader();
      reader.readAsDataURL(file);

      reader.onloadend = function () {
        let img = document.createElement('img');
        img.className = 'upload_img mt-2';
        img.setAttribute('alt', file.name);
        img.src = reader.result;

        let removeButton = document.createElement('button');
        removeButton.innerHTML = 'X';
        removeButton.classList.add('remove-button'); // Ajoutez la classe remove-button
        removeButton.addEventListener('click', () => removeImage(dataRefs, img));


        let container = document.createElement('div');
        container.appendChild(img);
        container.appendChild(removeButton);

        dataRefs.gallery.appendChild(container);
      }
    }
  }

  const imageUpload = dataRefs => {
    if (!dataRefs.files || !dataRefs.input) return;

    const url = dataRefs.input.getAttribute('data-post-url');
    if (!url) return;

    const name = dataRefs.input.getAttribute('data-post-name');
    if (!name) return;

    const formData = new FormData();
    formData.append(name, dataRefs.files);

    fetch(url, {
      method: 'POST',
      body: formData
    })
      .then(response => response.json())
      .then(data => {
        console.log('posted: ', data);
        if (data.success === true) {
          previewFiles(dataRefs);
        } else {
          console.log('URL: ', url, '  name: ', name)
        }
      })
      .catch(error => {
        console.error('errored: ', error);
      });
  }

const handleFiles = dataRefs => {
  let files = [...dataRefs.files];

  // Remove unaccepted file types
  files = files.filter(item => {
    if (!isImageFile(item)) {
      console.log('Not an image, ', item.type);
    }
    return isImageFile(item) ? item : null;
  });

  // Limit to 3 files
  if (files.length + dataRefs.gallery.childElementCount > 2) {
    const errorMessage = document.querySelector('.upload_errorMessage');
    errorMessage.textContent = 'Cannot upload more than 3 images.';
    errorMessage.style.display = 'block';
    return;
  }

  // Reset error message if there are no errors
  const errorMessage = document.querySelector('.upload_errorMessage');
  errorMessage.textContent = '';
  errorMessage.style.display = 'none';

  if (!files.length) return;
  dataRefs.files = files;

  previewFiles(dataRefs);
  imageUpload(dataRefs);
}

})();
