<?php

namespace App\Http\Controllers\Auth;

use App\Http\Controllers\Controller;
use App\Models\User;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\RedirectResponse;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Str;
use Laravel\Socialite\Facades\Socialite;
use Throwable;

class SocialiteController extends Controller
{
    /**
     * Provedores sociais suportados pelo stack.
     * Toda rota social valida o {provider} contra esta allowlist:
     * sem isso, o Socialite recebe qualquer string e estoura 500.
     */
    private const PROVIDERS = ['google', 'facebook'];

    /**
     * Lista apenas os provedores com credenciais configuradas em config/services.php.
     *
     * É este array (ex.: ['google', 'facebook']) que o frontend consome
     * via route('social.providers') para montar os botões do MaxAuthCard.
     * Provedor sem client_id/client_secret não aparece — botão não é exibido.
     */
    public function providers(): JsonResponse
    {
        $enabled = array_values(array_filter(self::PROVIDERS, function (string $provider) {
            return filled(config("services.$provider.client_id"))
                && filled(config("services.$provider.client_secret"));
        }));

        return response()->json($enabled);
    }

    /**
     * Inicia o fluxo OAuth: redireciona o navegador ao provedor.
     *
     * Chamado por navegação total do frontend:
     *   window.location.href = route('social.redirect', { provider })
     * Não é XHR — é um redirect do navegador.
     */
    public function redirect(string $provider): RedirectResponse
    {
        abort_unless(in_array($provider, self::PROVIDERS, true), 404);

        return Socialite::driver($provider)->redirect();
    }

    /**
     * Callback do provedor após o consentimento.
     *
     * Busca o usuário pelo e-mail; se for o primeiro acesso, CRIA a conta
     * automaticamente (firstOrCreate) com senha aleatória — a coluna password
     * é NOT NULL e a conta social nunca usa senha local. Em seguida abre a
     * SESSÃO (Auth::login com "remember") e redireciona para a app.
     *
     * Erros do OAuth e ausência de e-mail são tratados redirecionando ao
     * login com ?error=..., para o frontend exibir a mensagem.
     */
    public function callback(string $provider): RedirectResponse
    {
        abort_unless(in_array($provider, self::PROVIDERS, true), 404);

        try {
            $socialUser = Socialite::driver($provider)->user();
        } catch (Throwable $e) {
            return redirect('/login?error=oauth_error');
        }

        if (! $socialUser->getEmail()) {
            return redirect('/login?error=no_email');
        }

        // Find-or-create: primeiro acesso cria a conta automaticamente.
        $user = User::firstOrCreate(
            ['email' => $socialUser->getEmail()],
            [
                'name'              => $socialUser->getName()
                    ?? $socialUser->getNickname()
                    ?? 'Usuário',
                // Conta social: senha aleatória (cast 'hashed' no model faz o bcrypt).
                'password'          => Str::random(32),
                'email_verified_at' => now(),
            ]
        );

        // Autenticação por SESSÃO (guard web), com cookie de "lembrar-me".
        Auth::login($user, true);

        return redirect()->intended('/');
    }
}
