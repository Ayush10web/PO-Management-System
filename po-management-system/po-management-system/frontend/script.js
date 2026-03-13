let rowCount = 0;

async function loadDropdowns() {
  const vendors = await fetch('http://127.0.0.1:8000/vendors').then(r => r.json());
  vendors.forEach(v => $("#vendorSelect").append(`<option value="${v.id}">${v.name}</option>`));

  const products = await fetch('http://127.0.0.1:8000/products').then(r => r.json());
  window.allProducts = products;   // save globally
}

function addRow() {
  rowCount++;
  const row = `<tr id="row${rowCount}">
    <td><select class="product-select form-control" onchange="updatePrice(this)"></select></td>
    <td><input type="number" class="qty form-control" value="1" onchange="calculateLine(this)"></td>
    <td class="price">0</td>
    <td class="line-total">0</td>
    <td><button class="btn btn-danger btn-sm" onclick="deleteRow(this)">×</button></td>
    <td><button class="btn btn-info btn-sm" onclick="autoDescription(this)">AI Desc</button></td>
  </tr>`;
  $("#itemsTable tbody").append(row);

  // populate product dropdown
  window.allProducts.forEach(p => {
    $(`#row${rowCount} .product-select`).append(`<option value="${p.id}" data-price="${p.unit_price}">${p.name}</option>`);
  });
}

function updatePrice(select) {
  const price = $(select).find(":selected").data("price");
  $(select).closest("tr").find(".price").text(price);
  calculateLine(select);
}

function calculateLine(el) {
  const tr = $(el).closest("tr");
  const price = parseFloat(tr.find(".price").text());
  const qty = parseFloat(tr.find(".qty").val());
  const line = (price * qty).toFixed(2);
  tr.find(".line-total").text(line);
}

function autoDescription(btn) {
  const productName = $(btn).closest("tr").find("select option:selected").text();
  fetch(`http://127.0.0.1:8000/generate-desc?name=${encodeURIComponent(productName)}`)
    .then(r => r.json())
    .then(data => alert("AI Description:\n" + data.description));
}

async function submitPO() {
  // collect all rows and send to backend (standard fetch POST)
  // you can copy this part from any tutorial – very small
}