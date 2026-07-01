<?php
// wiring/routes-web.php
// Backend Laravel 13. Login por sessão (e-mail OU telefone) + Socialite.

use App\Http\Controllers\Auth\LoginController;
use App\Http\Controllers\Auth\SocialiteController;
use Illuminate\Support\Facades\Route;

Route::middleware('web')->group(function () {
    // Necessário para o front (MaxPinia/axios) obter o cookie XSRF-TOKEN.
    Route::get('/sanctum/csrf-cookie', fn () => response()->noContent());

    Route::post('/login', [LoginController::class, 'store'])->name('login');
    Route::post('/logout', [LoginController::class, 'destroy'])->name('logout');

    // OAuth social (Laravel Socialite)
    Route::get('/oauth/{provider}/redirect', [SocialiteController::class, 'redirect'])
        ->name('oauth.redirect');
    Route::get('/oauth/{provider}/callback', [SocialiteController::class, 'callback'])
        ->name('oauth.callback');
});
