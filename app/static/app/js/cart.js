var updateBtns = document.querySelectorAll('.update-cart');
var buyBtns = document.querySelectorAll('.buy-cart');

for (i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function () {
        var productId = this.dataset.product;
        var sizeId = this.dataset.size;
        var action = this.dataset.action;

        // Gán giá trị size_id từ button "size" tương ứng
        var sizeButtons = document.querySelectorAll('.size button');
        sizeButtons.forEach(function (sizeButton) {
            if (sizeButton.classList.contains('selected')) {
                sizeId = sizeButton.dataset.size;
            }
        });
        console.log('productId', productId, 'sizeId', sizeId, 'action', action);
        console.log('user ', user)
        if (user === "AnonymousUser") {
            displayAlert('Please log in to add products to cart.');
        } else {
            updateUserCart(productId, sizeId, action, false)
            location.reload()
        }
    })
}
for (i = 0; i < buyBtns.length; i++) {
    buyBtns[i].addEventListener('click', function () {
        var productId = this.dataset.product;
        var sizeId = this.dataset.size;
        var action = this.dataset.action;

        // Gán giá trị size_id từ button "size" tương ứng
        var sizeButtons = document.querySelectorAll('.size button');
        sizeButtons.forEach(function (sizeButton) {
            if (sizeButton.classList.contains('selected')) {
                sizeId = sizeButton.dataset.size;
            }
        });
        if (user === "AnonymousUser") {
            displayAlert('Please log in to add products to cart.');
        } else {
            updateUserCart(productId, sizeId, action, true);

        }
    })
}

function displayAlert(message) {
    var alertDiv = document.createElement('div');
    alertDiv.classList.add('alert', 'alert-danger');
    alertDiv.setAttribute('role', 'alert');
    alertDiv.innerHTML = message;
    alertContainer.appendChild(alertDiv);
    setTimeout(function () {
        alertDiv.remove();
    }, 5000); // Xóa thông báo sau 5 giây
}

function updateUserCart(productId, sizeId, action, redirectToCart) {
    productId = parseInt(productId);
    var url = '/updateitem/';
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ 'productId': productId, 'sizeId': sizeId, 'action': action })
    })
        .then((response) => { return response.json() })
        .then((data) => {
            console.log('data', data)
            if (redirectToCart) {
                location.reload()
                window.location.href = 'http://127.0.0.1:8000/cart/';
            } else {
                location.reload();
            }
        })
}
