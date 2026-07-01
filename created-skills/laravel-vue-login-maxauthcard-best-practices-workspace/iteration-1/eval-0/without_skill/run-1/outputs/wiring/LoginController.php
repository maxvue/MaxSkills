<?php
// wiring/LoginController.php
// app/Http/Controllers/Auth/LoginController.php

namespace App\Http\Controllers\Auth;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Validation\ValidationException;

class LoginController extends Controller
{
    public function store(Request $request)
    {
        $data = $request->validate([
            'login'    => ['required', 'string'],
            'password' => ['required', 'string'],
            'remember' => ['boolean'],
        ]);

        // Detecta se o usuário digitou e-mail ou telefone.
        $field = filter_var($data['login'], FILTER_VALIDATE_EMAIL) ? 'email' : 'phone';

        $credentials = [
            $field     => $data['login'],
            'password' => $data['password'],
        ];

        if (! Auth::attempt($credentials, $request->boolean('remember'))) {
            // 422 com a chave 'login' para o MaxAuthCard renderizar inline.
            throw ValidationException::withMessages([
                'login' => __('Credenciais inválidas.'),
            ]);
        }

        $request->session()->regenerate();

        return response()->json([
            'user' => $request->user()->only(['id', 'name', 'email', 'phone']),
        ]);
    }

    public function destroy(Request $request)
    {
        Auth::guard('web')->logout();
        $request->session()->invalidate();
        $request->session()->regenerateToken();

        return response()->noContent();
    }
}
