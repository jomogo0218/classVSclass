/**
 * Firebase Configuration for CHSH ClassVSClass
 */

const firebaseConfig = {
  apiKey: "AIzaSyAJCzaAAQrQ7IT933znHiNeo1R2ETvIdfI",
  authDomain: "classvsclass-ed238.firebaseapp.com",
  projectId: "classvsclass-ed238",
  storageBucket: "classvsclass-ed238.firebasestorage.app",
  messagingSenderId: "656997062034",
  appId: "1:656997062034:web:b1d4317b9fb1f405be5d4b",
  measurementId: "G-WFNM1ZWTXN"
};

// 初始化 Firebase (使用相容模式，適合您的 Vanilla JS 專案)
firebase.initializeApp(firebaseConfig);
const db = firebase.firestore();

// 讓 app.js 也能抓到資料庫物件
window.db = db;
