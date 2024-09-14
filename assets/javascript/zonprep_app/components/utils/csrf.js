const getCSRFToken = () => {
  let token = document.querySelector('input[name="csrfmiddlewaretoken"]');
  return token.value;
}

export {getCSRFToken};
