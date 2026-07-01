<?php

namespace App\Http\Controllers\Auth;

use App\Http\Controllers\Controller;
use App\Models\User;
use Illuminate\Http\RedirectResponse;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Str;
use Laravel\Socialite\Facades\Socialite;
use Laravel\Socialite\Two\InvalidStateException;

class SocialiteController extends Controller
{
    /**
     * Provedores OAuth permitidos.
     *
     * Restringir explicitamente evita que um parâmetro arbitrário
     * de rota acione drivers não configurados.
     *
     * @var array<int, string>
     */
    protected array $allowedProviders = ['google', 'facebook'];

    /**
     * Redireciona o usuário para a página de autenticação do provedor.
     *
     * GET /auth/{provider}/redirect  ->  name: auth.social.redirect
     */
    public function redirect(string $provider): RedirectResponse
    {
        $this->ensureProviderIsAllowed($provider);

        return Socialite::driver($provider)->redirect();
    }

    /**
     * Trata o callback do provedor: cria/atualiza o usuário e abre a sessão.
     *
     * GET /auth/{provider}/callback  ->  name: auth.social.callback
     */
    public function callback(string $provider): RedirectResponse
    {
        $this->ensureProviderIsAllowed($provider);

        try {
            // stateless() NÃO é usado: dependemos do state na sessão (guard web).
            $socialUser = Socialite::driver($provider)->user();
        } catch (InvalidStateException $e) {
            // State inválido normalmente significa sessão expirada ou CSRF.
            return redirect()
                ->route('login')
                ->withErrors(['social' => 'Falha na autenticação social. Tente novamente.']);
        }

        $user = $this->findOrCreateUser($provider, $socialUser);

        // Login por sessão no guard web.
        Auth::login($user, remember: true);

        // Boa prática pós-login: regenerar a sessão para evitar session fixation.
        request()->session()->regenerate();

        return redirect()->intended(route('dashboard'));
    }

    /**
     * Localiza um usuário existente pelo provider/id ou e-mail,
     * ou cria automaticamente no primeiro acesso.
     */
    protected function findOrCreateUser(string $provider, $socialUser): User
    {
        $providerId = (string) $socialUser->getId();
        $email = $socialUser->getEmail();

        // 1) Já vinculado a este provedor? Atualiza tokens e retorna.
        $user = User::query()
            ->where('provider', $provider)
            ->where('provider_id', $providerId)
            ->first();

        if ($user) {
            return tap($user)->update([
                'provider_token'         => $socialUser->token ?? null,
                'provider_refresh_token' => $socialUser->refreshToken ?? null,
                'avatar'                 => $socialUser->getAvatar() ?: $user->avatar,
            ]);
        }

        // 2) Já existe conta com o mesmo e-mail? Vincula o provedor a ela.
        if ($email) {
            $existing = User::query()->where('email', $email)->first();

            if ($existing) {
                return tap($existing)->update([
                    'provider'               => $provider,
                    'provider_id'            => $providerId,
                    'provider_token'         => $socialUser->token ?? null,
                    'provider_refresh_token' => $socialUser->refreshToken ?? null,
                    'avatar'                 => $existing->avatar ?: $socialUser->getAvatar(),
                ]);
            }
        }

        // 3) Primeiro acesso: cria o usuário automaticamente.
        return User::create([
            'name'                   => $socialUser->getName() ?: $socialUser->getNickname() ?: 'Usuário',
            'email'                  => $email,
            'email_verified_at'      => now(), // e-mail validado pelo provedor OAuth
            'password'               => bcrypt(Str::random(40)), // senha aleatória; login é só social
            'provider'               => $provider,
            'provider_id'            => $providerId,
            'provider_token'         => $socialUser->token ?? null,
            'provider_refresh_token' => $socialUser->refreshToken ?? null,
            'avatar'                 => $socialUser->getAvatar(),
        ]);
    }

    /**
     * Garante que o provedor solicitado é suportado.
     */
    protected function ensureProviderIsAllowed(string $provider): void
    {
        abort_unless(
            in_array($provider, $this->allowedProviders, true),
            404,
            "Provedor social não suportado: {$provider}"
        );
    }
}
