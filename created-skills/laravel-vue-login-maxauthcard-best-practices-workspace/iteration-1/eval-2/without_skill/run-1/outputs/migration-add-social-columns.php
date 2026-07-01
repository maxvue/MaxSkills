<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/*
|--------------------------------------------------------------------------
| Migration de apoio (colunas sociais na tabela users)
|--------------------------------------------------------------------------
|
| Necessária para o SocialiteController persistir provider/provider_id/tokens.
| Gere com:  php artisan make:migration add_social_columns_to_users_table
| e cole o conteúdo abaixo.
|
*/

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('users', function (Blueprint $table) {
            $table->string('provider')->nullable()->after('password');
            $table->string('provider_id')->nullable()->after('provider');
            $table->text('provider_token')->nullable()->after('provider_id');
            $table->text('provider_refresh_token')->nullable()->after('provider_token');
            $table->string('avatar')->nullable()->after('provider_refresh_token');

            // Um par (provider, provider_id) deve ser único.
            $table->unique(['provider', 'provider_id']);
        });
    }

    public function down(): void
    {
        Schema::table('users', function (Blueprint $table) {
            $table->dropUnique(['provider', 'provider_id']);
            $table->dropColumn([
                'provider',
                'provider_id',
                'provider_token',
                'provider_refresh_token',
                'avatar',
            ]);
        });
    }
};
