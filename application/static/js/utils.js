function toggleColorFields(checkboxId, colorFieldIds) {
    var checkbox = document.getElementById(checkboxId);
  
    colorFieldIds.forEach(function (colorFieldId) {
      var colorField = document.getElementById(colorFieldId);
      colorField.disabled = !checkbox.checked;
      colorField.value = checkbox.checked ? colorField.dataset.defaultValue : "";
    });
  }