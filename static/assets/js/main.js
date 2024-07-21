// OPEN & CLOSE CART
const cartIcon = document.querySelector("#cart-icon");
const cart = document.querySelector(".cart");
const closeCart = document.querySelector("#cart-close");

cartIcon.addEventListener("click", () => {
  cart.classList.add("active");
});

closeCart.addEventListener("click", () => {
  cart.classList.remove("active");
});

// Start when the document is ready
if (document.readyState == "loading") {
  document.addEventListener("DOMContentLoaded", start);
} else {
  start();
}

// =============== START ====================
function start() {
  addEvents();
}

// ============= UPDATE & RERENDER ===========
function update() {
  addEvents();
  updateTotal();
}

// =============== ADD EVENTS ===============
function addEvents() {
  // Remove items from cart
  let cartRemove_btns = document.querySelectorAll(".cart-remove");
  console.log(cartRemove_btns);
  cartRemove_btns.forEach((btn) => {
    btn.addEventListener("click", handle_removeCartItem);
  });

  // Change item quantity
  let cartQuantity_inputs = document.querySelectorAll(".cart-quantity");
  cartQuantity_inputs.forEach((input) => {
    input.addEventListener("change", handle_changeItemQuantity);
  });

  // Add item to cart
  let addCart_btns = document.querySelectorAll(".add-cart");
  addCart_btns.forEach((btn) => {
    btn.addEventListener("click", handle_addCartItem);
  });

  // Buy Order
  const buy_btn = document.querySelector(".btn-buy");
  buy_btn.addEventListener("click", handle_buyOrder);
}

// ============= HANDLE EVENTS FUNCTIONS =============
let itemsAdded = [];

function handle_addCartItem() {
  let product = this.parentElement;
  let title = product.querySelector(".product-title").innerHTML;
  let price = product.querySelector(".product-price").innerHTML;
  let imgSrc = product.querySelector(".product-img").src;
  let productID = product.getAttribute("data-product-id");
  console.log(title, price, imgSrc, productID);

  let newToAdd = {
    title,
    price,
    imgSrc,
    productID
  };

  // handle item is already exist
  if (itemsAdded.find((el) => el.title == newToAdd.title)) {
    alert("This Item Is Already Exist!");
    return;
  } else {
    itemsAdded.push(newToAdd);
  }

  // Add product to cart
  let cartBoxElement = CartBoxComponent(title, price, imgSrc);
  let newNode = document.createElement("div");
  newNode.innerHTML = cartBoxElement;
  const cartContent = cart.querySelector(".cart-content");
  cartContent.appendChild(newNode);

  update();
}

function handle_removeCartItem() {
  this.parentElement.remove();
  itemsAdded = itemsAdded.filter(
    (el) =>
      el.title !=
      this.parentElement.querySelector(".cart-product-title").innerHTML
  );

  update();
}

function handle_changeItemQuantity() {
  if (isNaN(this.value) || this.value < 1) {
    this.value = 1;
  }
  this.value = Math.floor(this.value); // to keep it integer

  update();
}
function openModal() {
  var modal = document.getElementById("myModal");
  modal.style.display = "flex";
}

// Modal'ı kapatma işlevi
function closeModal() {
  var modal = document.getElementById("myModal");
  modal.style.display = "none";
}

// Modal'daki kapatma butonuna tıklama işlevi
document.getElementsByClassName("close")[0].onclick = function() {
  closeModal();
}

// Kampanyaları gör butonuna tıklama işlevi
document.getElementById('campaignButton').addEventListener('click', function() {
  window.location.href = 'https://www.akbank.com/kampanyalar';
});
function handle_buyOrder() {
  if (itemsAdded.length <= 0) {
      alert("There is No Order to Place Yet! \nPlease Make an Order first.");
      return;
  }
  const cartContent = cart.querySelector(".cart-content");
  const totalElement = cart.querySelector(".total-price");

  let productIDs = itemsAdded.map(item => item.productID).join(",");
  let totalAmount = parseFloat(totalElement.innerHTML.replace("$", ""));
  let userId = 1; // Örnek id
  let category = "Teknology"; // Örnek kategori

  fetch('/add-expense', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify({
          user_id: userId,
          products_id: productIDs,
          total_amount: totalAmount,
          category: category
      })
  })
  .then(response => response.json())
  .then(data => {
      if (data.error) {
          alert(data.error);
      } else {
          openModal();
          itemsAdded = [];
          update();
      }
  })
  .catch(error => console.error('Error:', error));
}
// =========== UPDATE & RERENDER FUNCTIONS =========
function updateTotal() {
  let cartBoxes = document.querySelectorAll(".cart-box");
  const totalElement = cart.querySelector(".total-price");
  let total = 0;
  cartBoxes.forEach((cartBox) => {
    let priceElement = cartBox.querySelector(".cart-price");
    let price = parseFloat(priceElement.innerHTML.replace("$", ""));
    let quantity = cartBox.querySelector(".cart-quantity").value;
    total += price * quantity;
  });

  // keep 2 digits after the decimal point
  total = total.toFixed(2);
  totalElement.innerHTML = "$" + total;
}

// ============= HTML COMPONENTS =============
function CartBoxComponent(title, price, imgSrc) {
  return `
    <div class="cart-box">
        <img src=${imgSrc} alt="" class="cart-img">
        <div class="detail-box">
            <div class="cart-product-title">${title}</div>
            <div class="cart-price">${price}</div>
            <input type="number" value="1" class="cart-quantity">
        </div>
        <!-- REMOVE CART  -->
        <i class='bx bxs-trash-alt cart-remove'></i>
    </div>`;
}