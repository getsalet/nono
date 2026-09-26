<?php
/**
 * GeneratePress.
 *
 * Please do not make any edits to this file. All edits should be done in a child theme.
 *
 * @package GeneratePress
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit; // Exit if accessed directly.
}

// Set our theme version.
define( 'GENERATE_VERSION', '3.5.1' );

if ( ! function_exists( 'generate_setup' ) ) {
	add_action( 'after_setup_theme', 'generate_setup' );
	/**
	 * Sets up theme defaults and registers support for various WordPress features.
	 *
	 * @since 0.1
	 */
	function generate_setup() {
		// Make theme available for translation.
		load_theme_textdomain( 'generatepress' );

		// Add theme support for various features.
		add_theme_support( 'automatic-feed-links' );
		add_theme_support( 'post-thumbnails' );
		add_theme_support( 'post-formats', array( 'aside', 'image', 'video', 'quote', 'link', 'status' ) );
		add_theme_support( 'woocommerce' );
		add_theme_support( 'title-tag' );
		add_theme_support( 'html5', array( 'search-form', 'comment-form', 'comment-list', 'gallery', 'caption', 'script', 'style' ) );
		add_theme_support( 'customize-selective-refresh-widgets' );
		add_theme_support( 'align-wide' );
		add_theme_support( 'responsive-embeds' );

		$color_palette = generate_get_editor_color_palette();

		if ( ! empty( $color_palette ) ) {
			add_theme_support( 'editor-color-palette', $color_palette );
		}

		add_theme_support(
			'custom-logo',
			array(
				'height' => 70,
				'width' => 350,
				'flex-height' => true,
				'flex-width' => true,
			)
		);

		// Register primary menu.
		register_nav_menus(
			array(
				'primary' => __( 'Primary Menu', 'generatepress' ),
			)
		);

		/**
		 * Set the content width to something large
		 * We set a more accurate width in generate_smart_content_width()
		 */
		global $content_width;
		if ( ! isset( $content_width ) ) {
			$content_width = 1200; /* pixels */
		}

		// Add editor styles to the block editor.
		add_theme_support( 'editor-styles' );

		$editor_styles = apply_filters(
			'generate_editor_styles',
			array(
				'assets/css/admin/block-editor.css',
			)
		);

		add_editor_style( $editor_styles );
	}
}

/**
 * Get all necessary theme files
 */
$theme_dir = get_template_directory();

require $theme_dir . '/inc/theme-functions.php';
require $theme_dir . '/inc/defaults.php';
require $theme_dir . '/inc/class-css.php';
require $theme_dir . '/inc/css-output.php';
require $theme_dir . '/inc/general.php';
require $theme_dir . '/inc/customizer.php';
require $theme_dir . '/inc/markup.php';
require $theme_dir . '/inc/typography.php';
require $theme_dir . '/inc/plugin-compat.php';
require $theme_dir . '/inc/block-editor.php';
require $theme_dir . '/inc/class-typography.php';
require $theme_dir . '/inc/class-typography-migration.php';
require $theme_dir . '/inc/class-html-attributes.php';
require $theme_dir . '/inc/class-theme-update.php';
require $theme_dir . '/inc/class-rest.php';
require $theme_dir . '/inc/deprecated.php';

if ( is_admin() ) {
	require $theme_dir . '/inc/meta-box.php';
	require $theme_dir . '/inc/class-dashboard.php';
}

/**
 * Load our theme structure
 */
require $theme_dir . '/inc/structure/archives.php';
require $theme_dir . '/inc/structure/comments.php';
require $theme_dir . '/inc/structure/featured-images.php';
require $theme_dir . '/inc/structure/footer.php';
require $theme_dir . '/inc/structure/header.php';
require $theme_dir . '/inc/structure/navigation.php';
require $theme_dir . '/inc/structure/post-meta.php';
require $theme_dir . '/inc/structure/sidebars.php';
require $theme_dir . '/inc/structure/search-modal.php';

/**
 * Site-specific Navar customizations belong to the child theme.
 * Do not run the legacy block below when a child theme is active:
 * it duplicates WooCommerce/language hooks and can recurse through taxonomy filters.
 */
if ( get_template_directory() !== get_stylesheet_directory() ) {
    return;
}

//////////////////////////////////////////////////////////////////
add_filter('woocommerce_structured_data_product', 'add_fake_reviews_to_products', 20, 2);

function add_fake_reviews_to_products($markup, $product) {
    // بررسی اینکه محصول منتشر شده باشه
    if ($product->get_status() === 'publish') {
        $markup['aggregateRating'] = array(
            '@type'       => 'AggregateRating',
            'ratingValue' => '5',
            'reviewCount' => '10',
            'bestRating'  => '5',
            'worstRating' => '1',
        );
    }
    return $markup;
}
///////////////////////////
add_action('woocommerce_product_meta_end', 'navar_add_shipping_return_info_and_schema');
function navar_add_shipping_return_info_and_schema() {
    if (!is_product()) return;

    global $product;

    // اطلاعات محصول
    $product_name = $product->get_name();
    $product_url = get_permalink($product->get_id());
    $product_image = wp_get_attachment_url($product->get_image_id());
    $product_price = $product->get_price();
    $brand_name = 'AFP';
    $short_description = wp_strip_all_tags($product->get_short_description());
    $sku = $product->get_sku();

    // امتیازدهی
    $average_rating = $product->get_average_rating();
    $review_count = $product->get_review_count();

    echo '<div class="shipping-return-info" style="margin-top:15px;padding:15px;border:1px solid #ddd;border-radius:8px;font-size:15px;background:#fefefe">';
    echo '<p><strong>ارسال:</strong> از طریق باربری، حضوری یا راننده به سراسر کشور - هماهنگی بعد از سفارش</p>';
    echo '<p><strong>سیاست بازگشت:</strong> <a href="https://navar-abyari.ir/قوانین" target="_blank" style="color:#0073aa;">مشاهده قوانین بازگشت کالا</a></p>';
    echo '</div>';

    // اسکیما
    ?>
    <script type="application/ld+json">
    {
      "@context": "https://schema.org/",
      "@type": "Product",
      "name": "<?php echo esc_js($product_name); ?>",
      "image": ["<?php echo esc_url($product_image); ?>"],
      "description": "<?php echo esc_js($short_description); ?>",
      "sku": "<?php echo esc_js($sku); ?>",
      "brand": {
        "@type": "Brand",
        "name": "<?php echo esc_js($brand_name); ?>"
      },
      "offers": {
        "@type": "Offer",
        "url": "<?php echo esc_url($product_url); ?>",
        "priceCurrency": "IRR",
        "price": "<?php echo esc_js($product_price); ?>",
        "availability": "https://schema.org/InStock",
        "priceValidUntil": "2029-01-01",
        "shippingDetails": {
          "@type": "OfferShippingDetails",
          "deliveryTime": {
            "@type": "ShippingDeliveryTime",
            "handlingTime": {
              "@type": "QuantitativeValue",
              "value": 1,
              "unitCode": "d"
            },
            "transitTime": {
              "@type": "QuantitativeValue",
              "value": 1,
              "unitCode": "d"
            }
          },
          "shippingRate": {
            "@type": "MonetaryAmount",
            "value": "0",
            "currency": "IRR"
          },
          "shippingDestination": {
            "@type": "DefinedRegion",
            "addressCountry": "IR"
          }
        },
        "hasMerchantReturnPolicy": {
          "@type": "MerchantReturnPolicy",
          "url": "https://navar-abyari.ir/قوانین",
          "returnPolicyCategory": "https://schema.org/MerchantReturnFiniteReturnWindow",
          "merchantReturnDays": "7",
          "returnMethod": "https://schema.org/ReturnByMail",
          "returnFees": "https://schema.org/FreeReturn"
        },
        "areaServed": [
          {
            "@type": "Country",
            "name": "Iran"
          },
          {
            "@type": "Country",
            "name": "Iraq"
          },
          {
            "@type": "Country",
            "name": "Afghanistan"
          },
          {
            "@type": "Country",
            "name": "Tajikistan"
          }
        ]
      }
      <?php if ($review_count > 0 && $average_rating >= 1 && $average_rating <= 5): ?>,
      "aggregateRating": {
        "@type": "AggregateRating",
        "ratingValue": "<?php echo esc_js($average_rating); ?>",
        "reviewCount": "<?php echo esc_js($review_count); ?>",
        "bestRating": "5",
        "worstRating": "1"
      },
      "review": {
        "@type": "Review",
        "author": {
          "@type": "Person",
          "name": "baharlooi"
        },
        "datePublished": "2025-03-15",
        "reviewBody": "عالی",
        "name": "Review of <?php echo esc_js($product_name); ?>",
        "reviewRating": {
          "@type": "Rating",
          "ratingValue": "5",
          "bestRating": "5",
          "worstRating": "1"
        }
      }
      <?php endif; ?>
    }
    </script>
    <?php
}
////////////////////////////////////
// تغییر نام تب "توضیحات تکمیلی" به "مشخصات کالا"
add_filter( 'woocommerce_product_tabs', 'custom_rename_additional_info_tab', 98 );
function custom_rename_additional_info_tab( $tabs ) {
    if ( isset( $tabs['additional_information'] ) ) {
        $tabs['additional_information']['title'] = 'مشخصات کالا';
    }
    return $tabs;
}

//////////////////////////////////////////
add_action('woocommerce_after_single_product', 'show_random_posts_below_product', 20);

function show_random_posts_below_product() {
    if (!is_product()) return;

    // گرفتن 10 پست رندم
    $args = array(
        'posts_per_page' => 10,
        'orderby' => 'rand', // رندم کردن پست‌ها
        'post_status' => 'publish',
    );
    $random_posts = new WP_Query($args);

    // نمایش پست‌ها فقط اگر پست‌هایی وجود داشته باشه
    if ($random_posts->have_posts()) :
        echo '<div class="random-posts" style="margin-top: 40px;">';
        echo '<h2>مطالب پیشنهادی</h2>';
        echo '<div class="random-posts-wrapper">';
        
        // حلقه پست‌ها
        while ($random_posts->have_posts()) : $random_posts->the_post();
            ?>
            <div class="random-post-item">
                <a href="<?php the_permalink(); ?>" style="text-decoration: none; color: inherit;">
                    <?php if (has_post_thumbnail()) : ?>
                        <div class="post-thumbnail">
                            <?php the_post_thumbnail('medium', ['style' => 'width: 100%; height: 100%; object-fit: cover;']); ?>
                        </div>
                    <?php endif; ?>
                    <h3><?php the_title(); ?></h3>
                </a>
            </div>
            <?php
        endwhile;

        echo '</div>';
        echo '</div>';
    endif;

    wp_reset_postdata(); // بازنشانی داده‌های WP

    // اضافه کردن استایل‌های خاص صفحه محصول
    echo '<style>
        /* استایل عمومی برای پست‌ها */
        .random-posts-wrapper {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            justify-content: space-between;
        }

        /* استایل برای هر پست */
        .random-post-item {
            flex: 1 0 21%; /* در دسکتاپ، پست‌ها در پنج ستون قرار می‌گیرند */
            box-sizing: border-box;
            margin-bottom: 20px;
        }

        .random-post-item a {
            display: block;
            text-align: center;
            color: inherit;
            text-decoration: none;
        }

        /* تصویر پست */
        .random-post-item .post-thumbnail {
            width: 100%;
            height: 200px;
            overflow: hidden;
            margin-bottom: 10px;
        }

        /* عنوان پست */
        .random-post-item h3 {
            font-size: 16px;
            font-weight: bold;
            margin-top: 10px;
        }

        /* استایل ریسپانسیو برای موبایل */
        @media (max-width: 767px) {
            .random-post-item {
                flex: 1 0 100%; /* در موبایل، پست‌ها در یک ستون عمودی قرار می‌گیرند */
            }
        }
    </style>';
}
///////////////////////
function register_custom_post_types_and_taxonomies() {
    $custom_post_types = [
        'zahedan' => [
            'labels' => [
                'name' => _x('زاهدان', 'Post Type General Name', 'navartape'),
                'singular_name' => _x('zahedan', 'Post Type Singular Name', 'navartape'),
                'all_items' => __('همه صفحات تبلیغاتی زاهدان', 'navartape'),
                'add_new_item' => __('افزودن صفحه جدید', 'navartape'),
                'edit_item' => __('ویرایش', 'navartape'),
            ],
            'args' => [
                'description' => 'zahedan for software products and online',
                'supports' => ['title', 'editor', 'excerpt', 'author', 'thumbnail', 'comments', 'revisions', 'custom-fields'],
                'public' => true,
                'has_archive' => true,
                'menu_icon' => 'dashicons-admin-site-alt2',
                'show_in_rest' => true, // Added for REST API support
            ],
            'taxonomies' => [
                'categories' => [
                    'hierarchical' => true,
                    'labels' => [
                        'name' => _x('zahedan Categories', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New zahedan Category', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
                'tags' => [
                    'hierarchical' => false,
                    'labels' => [
                        'name' => _x('zahedan Tags', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New zahedan Tag', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
            ],
        ],
        'shahrekord' => [
            'labels' => [
                'name' => _x('شهرکرد', 'Post Type General Name', 'navartape'),
                'singular_name' => _x('shahrekord', 'Post Type Singular Name', 'navartape'),
                'all_items' => __('همه صفحات تبلیغاتی شهرکرد', 'navartape'),
                'add_new_item' => __('افزودن صفحه جدید', 'navartape'),
                'edit_item' => __('ویرایش', 'navartape'),
            ],
            'args' => [
                'description' => 'shahrekord for software products and online',
                'supports' => ['title', 'editor', 'excerpt', 'author', 'thumbnail', 'comments', 'revisions', 'custom-fields'],
                'public' => true,
                'has_archive' => true,
                'menu_icon' => 'dashicons-admin-site-alt2',
                'show_in_rest' => true, // Added for REST API support
            ],
            'taxonomies' => [
                'categories' => [
                    'hierarchical' => true,
                    'labels' => [
                        'name' => _x('shahrekord Categories', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New shahrekord Category', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
                'tags' => [
                    'hierarchical' => false,
                    'labels' => [
                        'name' => _x('shahrekord Tags', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New shahrekord Tag', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
            ],
        ],
        'arak' => [
            'labels' => [
                'name' => _x('اراک', 'Post Type General Name', 'navartape'),
                'singular_name' => _x('arak', 'Post Type Singular Name', 'navartape'),
                'all_items' => __('همه صفحات تبلیغاتی اراک', 'navartape'),
                'add_new_item' => __('افزودن صفحه جدید', 'navartape'),
                'edit_item' => __('ویرایش', 'navartape'),
            ],
            'args' => [
                'description' => 'arak for software products and online',
                'supports' => ['title', 'editor', 'excerpt', 'author', 'thumbnail', 'comments', 'revisions', 'custom-fields'],
                'public' => true,
                'has_archive' => true,
                'menu_icon' => 'dashicons-admin-site-alt2',
                'show_in_rest' => true, // Added for REST API support
            ],
            'taxonomies' => [
                'categories' => [
                    'hierarchical' => true,
                    'labels' => [
                        'name' => _x('arak Categories', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New arak Category', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
                'tags' => [
                    'hierarchical' => false,
                    'labels' => [
                        'name' => _x('arak Tags', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New arak Tag', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
            ],
        ],
        'qazvin' => [
            'labels' => [
                'name' => _x('قزوین', 'Post Type General Name', 'navartape'),
                'singular_name' => _x('qazvin', 'Post Type Singular Name', 'navartape'),
                'all_items' => __('همه صفحات تبلیغاتی قزوین', 'navartape'),
                'add_new_item' => __('افزودن صفحه جدید', 'navartape'),
                'edit_item' => __('ویرایش', 'navartape'),
            ],
            'args' => [
                'description' => 'qazvin for software products and online',
                'supports' => ['title', 'editor', 'excerpt', 'author', 'thumbnail', 'comments', 'revisions', 'custom-fields'],
                'public' => true,
                'has_archive' => true,
                'menu_icon' => 'dashicons-admin-site-alt2',
                'show_in_rest' => true, // Added for REST API support
            ],
            'taxonomies' => [
                'categories' => [
                    'hierarchical' => true,
                    'labels' => [
                        'name' => _x('qazvin Categories', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New qazvin Category', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
                'tags' => [
                    'hierarchical' => false,
                    'labels' => [
                        'name' => _x('qazvin Tags', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New qazvin Tag', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
            ],
        ],
        'ardabil' => [
            'labels' => [
                'name' => _x('اردبیل', 'Post Type General Name', 'navartape'),
                'singular_name' => _x('ardabil', 'Post Type Singular Name', 'navartape'),
                'all_items' => __('همه صفحات تبلیغاتی اردبیل', 'navartape'),
                'add_new_item' => __('افزودن صفحه جدید', 'navartape'),
                'edit_item' => __('ویرایش', 'navartape'),
            ],
            'args' => [
                'description' => 'ardabil for software products and online',
                'supports' => ['title', 'editor', 'excerpt', 'author', 'thumbnail', 'comments', 'revisions', 'custom-fields'],
                'public' => true,
                'has_archive' => true,
                'menu_icon' => 'dashicons-admin-site-alt2',
                'show_in_rest' => true, // Added for REST API support
            ],
            'taxonomies' => [
                'categories' => [
                    'hierarchical' => true,
                    'labels' => [
                        'name' => _x('ardabil Categories', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New ardabil Category', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
                'tags' => [
                    'hierarchical' => false,
                    'labels' => [
                        'name' => _x('ardabil Tags', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New ardabil Tag', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
            ],
        ],
        'yazd' => [
            'labels' => [
                'name' => _x('یزد', 'Post Type General Name', 'navartape'),
                'singular_name' => _x('yazd', 'Post Type Singular Name', 'navartape'),
                'all_items' => __('همه صفحات تبلیغاتی یزد', 'navartape'),
                'add_new_item' => __('افزودن صفحه جدید', 'navartape'),
                'edit_item' => __('ویرایش', 'navartape'),
            ],
            'args' => [
                'description' => 'yazd for software products and online',
                'supports' => ['title', 'editor', 'excerpt', 'author', 'thumbnail', 'comments', 'revisions', 'custom-fields'],
                'public' => true,
                'has_archive' => true,
                'menu_icon' => 'dashicons-admin-site-alt2',
                'show_in_rest' => true, // Added for REST API support
            ],
            'taxonomies' => [
                'categories' => [
                    'hierarchical' => true,
                    'labels' => [
                        'name' => _x('yazd Categories', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New yazd Category', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
                'tags' => [
                    'hierarchical' => false,
                    'labels' => [
                        'name' => _x('yazd Tags', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New yazd Tag', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
            ],
        ],
        'zanjan' => [
            'labels' => [
                'name' => _x('زنجان', 'Post Type General Name', 'navartape'),
                'singular_name' => _x('zanjan', 'Post Type Singular Name', 'navartape'),
                'all_items' => __('همه صفحات تبلیغاتی زنجان', 'navartape'),
                'add_new_item' => __('افزودن صفحه جدید', 'navartape'),
                'edit_item' => __('ویرایش', 'navartape'),
            ],
            'args' => [
                'description' => 'zanjan for software products and online',
                'supports' => ['title', 'editor', 'excerpt', 'author', 'thumbnail', 'comments', 'revisions', 'custom-fields'],
                'public' => true,
                'has_archive' => true,
                'menu_icon' => 'dashicons-admin-site-alt2',
                'show_in_rest' => true, // Added for REST API support
            ],
            'taxonomies' => [
                'categories' => [
                    'hierarchical' => true,
                    'labels' => [
                        'name' => _x('zanjan Categories', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New zanjan Category', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
                'tags' => [
                    'hierarchical' => false,
                    'labels' => [
                        'name' => _x('zanjan Tags', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New zanjan Tag', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
            ],
        ],
        'isfahan' => [
            'labels' => [
                'name' => _x('اصفهان', 'Post Type General Name', 'navartape'),
                'singular_name' => _x('isfahan', 'Post Type Singular Name', 'navartape'),
                'all_items' => __('همه صفحات تبلیغاتی اصفهان', 'navartape'),
                'add_new_item' => __('افزودن صفحه جدید', 'navartape'),
                'edit_item' => __('ویرایش', 'navartape'),
            ],
            'args' => [
                'description' => 'isfahan for software products and online',
                'supports' => ['title', 'editor', 'excerpt', 'author', 'thumbnail', 'comments', 'revisions', 'custom-fields'],
                'public' => true,
                'has_archive' => true,
                'menu_icon' => 'dashicons-admin-site-alt2',
                'show_in_rest' => true, // Added for REST API support
            ],
            'taxonomies' => [
                'categories' => [
                    'hierarchical' => true,
                    'labels' => [
                        'name' => _x('isfahan Categories', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New isfahan Category', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
                'tags' => [
                    'hierarchical' => false,
                    'labels' => [
                        'name' => _x('isfahan Tags', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New isfahan Tag', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
            ],
        ],
        'tehran' => [
            'labels' => [
                'name' => _x('تهران', 'Post Type General Name', 'navartape'),
                'singular_name' => _x('tehran', 'Post Type Singular Name', 'navartape'),
                'all_items' => __('همه صفحات تبلیغاتی تهران', 'navartape'),
                'add_new_item' => __('افزودن صفحه جدید', 'navartape'),
                'edit_item' => __('ویرایش', 'navartape'),
            ],
            'args' => [
                'description' => 'tehran for software products and online',
                'supports' => ['title', 'editor', 'excerpt', 'author', 'thumbnail', 'comments', 'revisions', 'custom-fields'],
                'public' => true,
                'has_archive' => true,
                'menu_icon' => 'dashicons-admin-site-alt2',
                'show_in_rest' => true, // Added for REST API support
            ],
            'taxonomies' => [
                'categories' => [
                    'hierarchical' => true,
                    'labels' => [
                        'name' => _x('tehran Categories', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New tehran Category', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
                'tags' => [
                    'hierarchical' => false,
                    'labels' => [
                        'name' => _x('tehran Tags', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New tehran Tag', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
            ],
        ],
        'shiraz' => [
            'labels' => [
                'name' => _x('شیراز', 'Post Type General Name', 'navartape'),
                'singular_name' => _x('shiraz', 'Post Type Singular Name', 'navartape'),
                'all_items' => __('همه صفحات تبلیغاتی شیراز', 'navartape'),
                'add_new_item' => __('افزودن صفحه جدید', 'navartape'),
                'edit_item' => __('ویرایش', 'navartape'),
            ],
            'args' => [
                'description' => 'shiraz for software products and online',
                'supports' => ['title', 'editor', 'excerpt', 'author', 'thumbnail', 'comments', 'revisions', 'custom-fields'],
                'public' => true,
                'has_archive' => true,
                'menu_icon' => 'dashicons-admin-site-alt2',
                'show_in_rest' => true, // Added for REST API support
            ],
            'taxonomies' => [
                'categories' => [
                    'hierarchical' => true,
                    'labels' => [
                        'name' => _x('shiraz Categories', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New shiraz Category', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
                'tags' => [
                    'hierarchical' => false,
                    'labels' => [
                        'name' => _x('shiraz Tags', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New shiraz Tag', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
            ],
        ],
        'mashhad' => [
            'labels' => [
                'name' => _x('مشهد', 'Post Type General Name', 'navartape'),
                'singular_name' => _x('mashhad', 'Post Type Singular Name', 'navartape'),
                'all_items' => __('همه صفحات تبلیغاتی مشهد', 'navartape'),
                'add_new_item' => __('افزودن صفحه جدید', 'navartape'),
                'edit_item' => __('ویرایش', 'navartape'),
            ],
            'args' => [
                'description' => 'mashhad for software products and online',
                'supports' => ['title', 'editor', 'excerpt', 'author', 'thumbnail', 'comments', 'revisions', 'custom-fields'],
                'public' => true,
                'has_archive' => true,
                'menu_icon' => 'dashicons-admin-site-alt2',
                'show_in_rest' => true, // Added for REST API support
            ],
            'taxonomies' => [
                'categories' => [
                    'hierarchical' => true,
                    'labels' => [
                        'name' => _x('mashhad Categories', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New mashhad Category', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
                'tags' => [
                    'hierarchical' => false,
                    'labels' => [
                        'name' => _x('mashhad Tags', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New mashhad Tag', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
            ],
        ],
        'ahvaz' => [
            'labels' => [
                'name' => _x('اهواز', 'Post Type General Name', 'navartape'),
                'singular_name' => _x('ahvaz', 'Post Type Singular Name', 'navartape'),
                'all_items' => __('همه صفحات تبلیغاتی اهواز', 'navartape'),
                'add_new_item' => __('افزودن صفحه جدید', 'navartape'),
                'edit_item' => __('ویرایش', 'navartape'),
            ],
            'args' => [
                'description' => 'ahvaz for software products and online',
                'supports' => ['title', 'editor', 'excerpt', 'author', 'thumbnail', 'comments', 'revisions', 'custom-fields'],
                'public' => true,
                'has_archive' => true,
                'menu_icon' => 'dashicons-admin-site-alt2',
                'show_in_rest' => true, // Added for REST API support
            ],
            'taxonomies' => [
                'categories' => [
                    'hierarchical' => true,
                    'labels' => [
                        'name' => _x('ahvaz Categories', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New ahvaz Category', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
                'tags' => [
                    'hierarchical' => false,
                    'labels' => [
                        'name' => _x('ahvaz Tags', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New ahvaz Tag', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
            ],
        ],
        'hamadan' => [
            'labels' => [
                'name' => _x('همدان', 'Post Type General Name', 'navartape'),
                'singular_name' => _x('hamadan', 'Post Type Singular Name', 'navartape'),
                'all_items' => __('همه صفحات تبلیغاتی همدان', 'navartape'),
                'add_new_item' => __('افزودن صفحه جدید', 'navartape'),
                'edit_item' => __('ویرایش', 'navartape'),
            ],
            'args' => [
                'description' => 'hamadan for software products and online',
                'supports' => ['title', 'editor', 'excerpt', 'author', 'thumbnail', 'comments', 'revisions', 'custom-fields'],
                'public' => true,
                'has_archive' => true,
                'menu_icon' => 'dashicons-admin-site-alt2',
                'show_in_rest' => true, // Added for REST API support
            ],
            'taxonomies' => [
                'categories' => [
                    'hierarchical' => true,
                    'labels' => [
                        'name' => _x('hamadan Categories', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New hamadan Category', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
                'tags' => [
                    'hierarchical' => false,
                    'labels' => [
                        'name' => _x('hamadan Tags', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New hamadan Tag', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
            ],
        ],
        'kurdistan' => [
            'labels' => [
                'name' => _x('کردستان', 'Post Type General Name', 'navartape'),
                'singular_name' => _x('kurdistan', 'Post Type Singular Name', 'navartape'),
                'all_items' => __('همه صفحات تبلیغاتی کردستان', 'navartape'),
                'add_new_item' => __('افزودن صفحه جدید', 'navartape'),
                'edit_item' => __('ویرایش', 'navartape'),
            ],
            'args' => [
                'description' => 'kurdistan for software products and online',
                'supports' => ['title', 'editor', 'excerpt', 'author', 'thumbnail', 'comments', 'revisions', 'custom-fields'],
                'public' => true,
                'has_archive' => true,
                'menu_icon' => 'dashicons-admin-site-alt2',
                'show_in_rest' => true, // Added for REST API support
            ],
            'taxonomies' => [
                'categories' => [
                    'hierarchical' => true,
                    'labels' => [
                        'name' => _x('kurdistan Categories', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New kurdistan Category', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
                'tags' => [
                    'hierarchical' => false,
                    'labels' => [
                        'name' => _x('kurdistan Tags', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New kurdistan Tag', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
            ],
        ],
        'karaj' => [
            'labels' => [
                'name' => _x('کرج', 'Post Type General Name', 'navartape'),
                'singular_name' => _x('karaj', 'Post Type Singular Name', 'navartape'),
                'all_items' => __('همه صفحات تبلیغاتی کرج', 'navartape'),
                'add_new_item' => __('افزودن صفحه جدید', 'navartape'),
                'edit_item' => __('ویرایش', 'navartape'),
            ],
            'args' => [
                'description' => 'karaj for software products and online',
                'supports' => ['title', 'editor', 'excerpt', 'author', 'thumbnail', 'comments', 'revisions', 'custom-fields'],
                'public' => true,
                'has_archive' => true,
                'menu_icon' => 'dashicons-admin-site-alt2',
                'show_in_rest' => true, // Added for REST API support
            ],
            'taxonomies' => [
                'categories' => [
                    'hierarchical' => true,
                    'labels' => [
                        'name' => _x('karaj Categories', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New karaj Category', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
                'tags' => [
                    'hierarchical' => false,
                    'labels' => [
                        'name' => _x('karaj Tags', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New karaj Tag', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
            ],
        ],
        'bandarabbas' => [
            'labels' => [
                'name' => _x('بندرعباس', 'Post Type General Name', 'navartape'),
                'singular_name' => _x('bandarabbas', 'Post Type Singular Name', 'navartape'),
                'all_items' => __('همه صفحات تبلیغاتی بندرعباس', 'navartape'),
                'add_new_item' => __('افزودن صفحه جدید', 'navartape'),
                'edit_item' => __('ویرایش', 'navartape'),
            ],
            'args' => [
                'description' => 'bandarabbas for software products and online',
                'supports' => ['title', 'editor', 'excerpt', 'author', 'thumbnail', 'comments', 'revisions', 'custom-fields'],
                'public' => true,
                'has_archive' => true,
                'menu_icon' => 'dashicons-admin-site-alt2',
                'show_in_rest' => true, // Added for REST API support
            ],
            'taxonomies' => [
                'categories' => [
                    'hierarchical' => true,
                    'labels' => [
                        'name' => _x('bandarabbas Categories', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New bandarabbas Category', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
                'tags' => [
                    'hierarchical' => false,
                    'labels' => [
                        'name' => _x('bandarabbas Tags', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New bandarabbas Tag', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
            ],
        ],
        'bushehr' => [
            'labels' => [
                'name' => _x('بوشهر', 'Post Type General Name', 'navartape'),
                'singular_name' => _x('bushehr', 'Post Type Singular Name', 'navartape'),
                'all_items' => __('همه صفحات تبلیغاتی بوشهر', 'navartape'),
                'add_new_item' => __('افزودن صفحه جدید', 'navartape'),
                'edit_item' => __('ویرایش', 'navartape'),
            ],
            'args' => [
                'description' => 'bushehr for software products and online',
                'supports' => ['title', 'editor', 'excerpt', 'author', 'thumbnail', 'comments', 'revisions', 'custom-fields'],
                'public' => true,
                'has_archive' => true,
                'menu_icon' => 'dashicons-admin-site-alt2',
                'show_in_rest' => true, // Added for REST API support
            ],
            'taxonomies' => [
                'categories' => [
                    'hierarchical' => true,
                    'labels' => [
                        'name' => _x('bushehr Categories', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New bushehr Category', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
                'tags' => [
                    'hierarchical' => false,
                    'labels' => [
                        'name' => _x('bushehr Tags', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New bushehr Tag', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
            ],
        ],
        'semnan' => [
            'labels' => [
                'name' => _x('سمنان', 'Post Type General Name', 'navartape'),
                'singular_name' => _x('semnan', 'Post Type Singular Name', 'navartape'),
                'all_items' => __('همه صفحات تبلیغاتی سمنان', 'navartape'),
                'add_new_item' => __('افزودن صفحه جدید', 'navartape'),
                'edit_item' => __('ویرایش', 'navartape'),
            ],
            'args' => [
                'description' => 'semnan for software products and online',
                'supports' => ['title', 'editor', 'excerpt', 'author', 'thumbnail', 'comments', 'revisions', 'custom-fields'],
                'public' => true,
                'has_archive' => true,
                'menu_icon' => 'dashicons-admin-site-alt2',
                'show_in_rest' => true, // Added for REST API support
            ],
            'taxonomies' => [
                'categories' => [
                    'hierarchical' => true,
                    'labels' => [
                        'name' => _x('semnan Categories', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New semnan Category', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
                'tags' => [
                    'hierarchical' => false,
                    'labels' => [
                        'name' => _x('semnan Tags', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New semnan Tag', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
            ],
        ],
        'golestan' => [
            'labels' => [
                'name' => _x('گلستان', 'Post Type General Name', 'navartape'),
                'singular_name' => _x('golestan', 'Post Type Singular Name', 'navartape'),
                'all_items' => __('همه صفحات تبلیغاتی گلستان', 'navartape'),
                'add_new_item' => __('افزودن صفحه جدید', 'navartape'),
                'edit_item' => __('ویرایش', 'navartape'),
            ],
            'args' => [
                'description' => 'golestan for software products and online',
                'supports' => ['title', 'editor', 'excerpt', 'author', 'thumbnail', 'comments', 'revisions', 'custom-fields'],
                'public' => true,
                'has_archive' => true,
                'menu_icon' => 'dashicons-admin-site-alt2',
                'show_in_rest' => true, // Added for REST API support
            ],
            'taxonomies' => [
                'categories' => [
                    'hierarchical' => true,
                    'labels' => [
                        'name' => _x('golestan Categories', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New golestan Category', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
                'tags' => [
                    'hierarchical' => false,
                    'labels' => [
                        'name' => _x('golestan Tags', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New golestan Tag', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
            ],
        ],
        'gilan' => [
            'labels' => [
                'name' => _x('گیلان', 'Post Type General Name', 'navartape'),
                'singular_name' => _x('gilan', 'Post Type Singular Name', 'navartape'),
                'all_items' => __('همه صفحات تبلیغاتی گیلان', 'navartape'),
                'add_new_item' => __('افزودن صفحه جدید', 'navartape'),
                'edit_item' => __('ویرایش', 'navartape'),
            ],
            'args' => [
                'description' => 'gilan for software products and online',
                'supports' => ['title', 'editor', 'excerpt', 'author', 'thumbnail', 'comments', 'revisions', 'custom-fields'],
                'public' => true,
                'has_archive' => true,
                'menu_icon' => 'dashicons-admin-site-alt2',
                'show_in_rest' => true, // Added for REST API support
            ],
            'taxonomies' => [
                'categories' => [
                    'hierarchical' => true,
                    'labels' => [
                        'name' => _x('gilan Categories', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New gilan Category', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
                'tags' => [
                    'hierarchical' => false,
                    'labels' => [
                        'name' => _x('gilan Tags', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New gilan Tag', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
            ],
        ],
        'mazandaran' => [
            'labels' => [
                'name' => _x('مازندران', 'Post Type General Name', 'navartape'),
                'singular_name' => _x('mazandaran', 'Post Type Singular Name', 'navartape'),
                'all_items' => __('همه صفحات تبلیغاتی مازندران', 'navartape'),
                'add_new_item' => __('افزودن صفحه جدید', 'navartape'),
                'edit_item' => __('ویرایش', 'navartape'),
            ],
            'args' => [
                'description' => 'mazandaran for software products and online',
                'supports' => ['title', 'editor', 'excerpt', 'author', 'thumbnail', 'comments', 'revisions', 'custom-fields'],
                'public' => true,
                'has_archive' => true,
                'menu_icon' => 'dashicons-admin-site-alt2',
                'show_in_rest' => true, // Added for REST API support
            ],
            'taxonomies' => [
                'categories' => [
                    'hierarchical' => true,
                    'labels' => [
                        'name' => _x('mazandaran Categories', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New mazandaran Category', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
                'tags' => [
                    'hierarchical' => false,
                    'labels' => [
                        'name' => _x('mazandaran Tags', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New mazandaran Tag', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
            ],
        ],
        'orumiyeh' => [
            'labels' => [
                'name' => _x('ارومیه', 'Post Type General Name', 'navartape'),
                'singular_name' => _x('orumiyeh', 'Post Type Singular Name', 'navartape'),
                'all_items' => __('همه صفحات تبلیغاتی ارومیه', 'navartape'),
                'add_new_item' => __('افزودن صفحه جدید', 'navartape'),
                'edit_item' => __('ویرایش', 'navartape'),
            ],
            'args' => [
                'description' => 'orumiyeh for software products and online',
                'supports' => ['title', 'editor', 'excerpt', 'author', 'thumbnail', 'comments', 'revisions', 'custom-fields'],
                'public' => true,
                'has_archive' => true,
                'menu_icon' => 'dashicons-admin-site-alt2',
                'show_in_rest' => true, // Added for REST API support
            ],
            'taxonomies' => [
                'categories' => [
                    'hierarchical' => true,
                    'labels' => [
                        'name' => _x('orumiyeh Categories', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New orumiyeh Category', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
                'tags' => [
                    'hierarchical' => false,
                    'labels' => [
                        'name' => _x('orumiyeh Tags', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New orumiyeh Tag', 'navartape'),
                    ],
                    'show_in_rest' => true, // Added for REST API support
                ],
            ],
        ],
        'east_azarbaijan' => [
            'labels' => [
                'name' => _x('آذربایجان شرقی', 'Post Type General Name', 'navartape'),
                'singular_name' => _x('east_azarbaijan', 'Post Type Singular Name', 'navartape'),
                'all_items' => __('همه صفحات تبلیغاتی آذربایجان شرقی', 'navartape'),
                'add_new_item' => __('افزودن صفحه جدید', 'navartape'),
                'edit_item' => __('ویرایش', 'navartape'),
            ],
            'args' => [
                'description' => 'آذربایجان شرقی promotional city pages',
                'supports' => ['title', 'editor', 'excerpt', 'author', 'thumbnail', 'comments', 'revisions', 'custom-fields'],
                'public' => true,
                'has_archive' => true,
                'menu_icon' => 'dashicons-admin-site-alt2',
                'show_in_rest' => true,
            ],
            'taxonomies' => [
                'categories' => [
                    'hierarchical' => true,
                    'labels' => [
                        'name' => _x('آذربایجان شرقی Categories', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New آذربایجان شرقی Category', 'navartape'),
                    ],
                    'show_in_rest' => true,
                ],
                'tags' => [
                    'hierarchical' => false,
                    'labels' => [
                        'name' => _x('آذربایجان شرقی Tags', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New آذربایجان شرقی Tag', 'navartape'),
                    ],
                    'show_in_rest' => true,
                ],
            ],
        ],
        'kermanshah' => [
            'labels' => [
                'name' => _x('کرمانشاه', 'Post Type General Name', 'navartape'),
                'singular_name' => _x('kermanshah', 'Post Type Singular Name', 'navartape'),
                'all_items' => __('همه صفحات تبلیغاتی کرمانشاه', 'navartape'),
                'add_new_item' => __('افزودن صفحه جدید', 'navartape'),
                'edit_item' => __('ویرایش', 'navartape'),
            ],
            'args' => [
                'description' => 'کرمانشاه promotional city pages',
                'supports' => ['title', 'editor', 'excerpt', 'author', 'thumbnail', 'comments', 'revisions', 'custom-fields'],
                'public' => true,
                'has_archive' => true,
                'menu_icon' => 'dashicons-admin-site-alt2',
                'show_in_rest' => true,
            ],
            'taxonomies' => [
                'categories' => [
                    'hierarchical' => true,
                    'labels' => [
                        'name' => _x('کرمانشاه Categories', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New کرمانشاه Category', 'navartape'),
                    ],
                    'show_in_rest' => true,
                ],
                'tags' => [
                    'hierarchical' => false,
                    'labels' => [
                        'name' => _x('کرمانشاه Tags', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New کرمانشاه Tag', 'navartape'),
                    ],
                    'show_in_rest' => true,
                ],
            ],
        ],
        'kerman' => [
            'labels' => [
                'name' => _x('کرمان', 'Post Type General Name', 'navartape'),
                'singular_name' => _x('kerman', 'Post Type Singular Name', 'navartape'),
                'all_items' => __('همه صفحات تبلیغاتی کرمان', 'navartape'),
                'add_new_item' => __('افزودن صفحه جدید', 'navartape'),
                'edit_item' => __('ویرایش', 'navartape'),
            ],
            'args' => [
                'description' => 'کرمان promotional city pages',
                'supports' => ['title', 'editor', 'excerpt', 'author', 'thumbnail', 'comments', 'revisions', 'custom-fields'],
                'public' => true,
                'has_archive' => true,
                'menu_icon' => 'dashicons-admin-site-alt2',
                'show_in_rest' => true,
            ],
            'taxonomies' => [
                'categories' => [
                    'hierarchical' => true,
                    'labels' => [
                        'name' => _x('کرمان Categories', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New کرمان Category', 'navartape'),
                    ],
                    'show_in_rest' => true,
                ],
                'tags' => [
                    'hierarchical' => false,
                    'labels' => [
                        'name' => _x('کرمان Tags', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New کرمان Tag', 'navartape'),
                    ],
                    'show_in_rest' => true,
                ],
            ],
        ],
        'lorestan' => [
            'labels' => [
                'name' => _x('لرستان', 'Post Type General Name', 'navartape'),
                'singular_name' => _x('lorestan', 'Post Type Singular Name', 'navartape'),
                'all_items' => __('همه صفحات تبلیغاتی لرستان', 'navartape'),
                'add_new_item' => __('افزودن صفحه جدید', 'navartape'),
                'edit_item' => __('ویرایش', 'navartape'),
            ],
            'args' => [
                'description' => 'لرستان promotional city pages',
                'supports' => ['title', 'editor', 'excerpt', 'author', 'thumbnail', 'comments', 'revisions', 'custom-fields'],
                'public' => true,
                'has_archive' => true,
                'menu_icon' => 'dashicons-admin-site-alt2',
                'show_in_rest' => true,
            ],
            'taxonomies' => [
                'categories' => [
                    'hierarchical' => true,
                    'labels' => [
                        'name' => _x('لرستان Categories', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New لرستان Category', 'navartape'),
                    ],
                    'show_in_rest' => true,
                ],
                'tags' => [
                    'hierarchical' => false,
                    'labels' => [
                        'name' => _x('لرستان Tags', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New لرستان Tag', 'navartape'),
                    ],
                    'show_in_rest' => true,
                ],
            ],
        ],
        'ilam' => [
            'labels' => [
                'name' => _x('ایلام', 'Post Type General Name', 'navartape'),
                'singular_name' => _x('ilam', 'Post Type Singular Name', 'navartape'),
                'all_items' => __('همه صفحات تبلیغاتی ایلام', 'navartape'),
                'add_new_item' => __('افزودن صفحه جدید', 'navartape'),
                'edit_item' => __('ویرایش', 'navartape'),
            ],
            'args' => [
                'description' => 'ایلام promotional city pages',
                'supports' => ['title', 'editor', 'excerpt', 'author', 'thumbnail', 'comments', 'revisions', 'custom-fields'],
                'public' => true,
                'has_archive' => true,
                'menu_icon' => 'dashicons-admin-site-alt2',
                'show_in_rest' => true,
            ],
            'taxonomies' => [
                'categories' => [
                    'hierarchical' => true,
                    'labels' => [
                        'name' => _x('ایلام Categories', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New ایلام Category', 'navartape'),
                    ],
                    'show_in_rest' => true,
                ],
                'tags' => [
                    'hierarchical' => false,
                    'labels' => [
                        'name' => _x('ایلام Tags', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New ایلام Tag', 'navartape'),
                    ],
                    'show_in_rest' => true,
                ],
            ],
        ],
        'kohgiluyeh' => [
            'labels' => [
                'name' => _x('کهگیلویه و بویراحمد', 'Post Type General Name', 'navartape'),
                'singular_name' => _x('kohgiluyeh', 'Post Type Singular Name', 'navartape'),
                'all_items' => __('همه صفحات تبلیغاتی کهگیلویه و بویراحمد', 'navartape'),
                'add_new_item' => __('افزودن صفحه جدید', 'navartape'),
                'edit_item' => __('ویرایش', 'navartape'),
            ],
            'args' => [
                'description' => 'کهگیلویه و بویراحمد promotional city pages',
                'supports' => ['title', 'editor', 'excerpt', 'author', 'thumbnail', 'comments', 'revisions', 'custom-fields'],
                'public' => true,
                'has_archive' => true,
                'menu_icon' => 'dashicons-admin-site-alt2',
                'show_in_rest' => true,
            ],
            'taxonomies' => [
                'categories' => [
                    'hierarchical' => true,
                    'labels' => [
                        'name' => _x('کهگیلویه و بویراحمد Categories', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New کهگیلویه و بویراحمد Category', 'navartape'),
                    ],
                    'show_in_rest' => true,
                ],
                'tags' => [
                    'hierarchical' => false,
                    'labels' => [
                        'name' => _x('کهگیلویه و بویراحمد Tags', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New کهگیلویه و بویراحمد Tag', 'navartape'),
                    ],
                    'show_in_rest' => true,
                ],
            ],
        ],
        'qom' => [
            'labels' => [
                'name' => _x('قم', 'Post Type General Name', 'navartape'),
                'singular_name' => _x('qom', 'Post Type Singular Name', 'navartape'),
                'all_items' => __('همه صفحات تبلیغاتی قم', 'navartape'),
                'add_new_item' => __('افزودن صفحه جدید', 'navartape'),
                'edit_item' => __('ویرایش', 'navartape'),
            ],
            'args' => [
                'description' => 'قم promotional city pages',
                'supports' => ['title', 'editor', 'excerpt', 'author', 'thumbnail', 'comments', 'revisions', 'custom-fields'],
                'public' => true,
                'has_archive' => true,
                'menu_icon' => 'dashicons-admin-site-alt2',
                'show_in_rest' => true,
            ],
            'taxonomies' => [
                'categories' => [
                    'hierarchical' => true,
                    'labels' => [
                        'name' => _x('قم Categories', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New قم Category', 'navartape'),
                    ],
                    'show_in_rest' => true,
                ],
                'tags' => [
                    'hierarchical' => false,
                    'labels' => [
                        'name' => _x('قم Tags', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New قم Tag', 'navartape'),
                    ],
                    'show_in_rest' => true,
                ],
            ],
        ],
        'north_khorasan' => [
            'labels' => [
                'name' => _x('خراسان شمالی', 'Post Type General Name', 'navartape'),
                'singular_name' => _x('north_khorasan', 'Post Type Singular Name', 'navartape'),
                'all_items' => __('همه صفحات تبلیغاتی خراسان شمالی', 'navartape'),
                'add_new_item' => __('افزودن صفحه جدید', 'navartape'),
                'edit_item' => __('ویرایش', 'navartape'),
            ],
            'args' => [
                'description' => 'خراسان شمالی promotional city pages',
                'supports' => ['title', 'editor', 'excerpt', 'author', 'thumbnail', 'comments', 'revisions', 'custom-fields'],
                'public' => true,
                'has_archive' => true,
                'menu_icon' => 'dashicons-admin-site-alt2',
                'show_in_rest' => true,
            ],
            'taxonomies' => [
                'categories' => [
                    'hierarchical' => true,
                    'labels' => [
                        'name' => _x('خراسان شمالی Categories', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New خراسان شمالی Category', 'navartape'),
                    ],
                    'show_in_rest' => true,
                ],
                'tags' => [
                    'hierarchical' => false,
                    'labels' => [
                        'name' => _x('خراسان شمالی Tags', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New خراسان شمالی Tag', 'navartape'),
                    ],
                    'show_in_rest' => true,
                ],
            ],
        ],
        'south_khorasan' => [
            'labels' => [
                'name' => _x('خراسان جنوبی', 'Post Type General Name', 'navartape'),
                'singular_name' => _x('south_khorasan', 'Post Type Singular Name', 'navartape'),
                'all_items' => __('همه صفحات تبلیغاتی خراسان جنوبی', 'navartape'),
                'add_new_item' => __('افزودن صفحه جدید', 'navartape'),
                'edit_item' => __('ویرایش', 'navartape'),
            ],
            'args' => [
                'description' => 'خراسان جنوبی promotional city pages',
                'supports' => ['title', 'editor', 'excerpt', 'author', 'thumbnail', 'comments', 'revisions', 'custom-fields'],
                'public' => true,
                'has_archive' => true,
                'menu_icon' => 'dashicons-admin-site-alt2',
                'show_in_rest' => true,
            ],
            'taxonomies' => [
                'categories' => [
                    'hierarchical' => true,
                    'labels' => [
                        'name' => _x('خراسان جنوبی Categories', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New خراسان جنوبی Category', 'navartape'),
                    ],
                    'show_in_rest' => true,
                ],
                'tags' => [
                    'hierarchical' => false,
                    'labels' => [
                        'name' => _x('خراسان جنوبی Tags', 'taxonomy general name', 'navartape'),
                        'add_new_item' => __('Add New خراسان جنوبی Tag', 'navartape'),
                    ],
                    'show_in_rest' => true,
                ],
            ],
        ],
    ];

    foreach ($custom_post_types as $post_type => $data) {
        $labels = $data['labels'];
        $args = array_merge([
            'labels' => $labels,
            'public' => true,
            'show_ui' => true,
            'show_in_menu' => true,
            'show_in_rest' => true, // Added for REST API support
        ], $data['args']);
        register_post_type($post_type, $args);

        if (!empty($data['taxonomies'])) {
            foreach ($data['taxonomies'] as $taxonomy => $taxonomy_data) {
                $taxonomy_labels = $taxonomy_data['labels'];
                $taxonomy_args = array_merge([
                    'labels' => $taxonomy_labels,
                    'public' => true,
                    'show_ui' => true,
                    'show_in_rest' => true, // Added for REST API support
                ], $taxonomy_data);
                register_taxonomy("{$post_type}_{$taxonomy}", [$post_type], $taxonomy_args);
            }
        }
    }
}
add_action('init', 'register_custom_post_types_and_taxonomies');


//////////////////////////////////////////////////////////////////////////////
function disable_gutenberg_styles() {
    wp_dequeue_style('wp-block-library');
    wp_dequeue_style('wp-block-library-theme');
    wp_dequeue_style('wc-blocks-style');
}
add_action('wp_enqueue_scripts', 'disable_gutenberg_styles', 100);
add_action('admin_enqueue_scripts', 'disable_gutenberg_styles', 100);

///////////////////////

add_filter( 'wp_is_application_passwords_available', '__return_true' );
//////////////////////////////

// ✅ اجازه نمایش meta در REST API برای همه پست تایپ‌ها
add_action('rest_api_init', function () {
    $post_types = [
        'post',
        'zahedan',
        'shahrekord',
        'arak',
        'qazvin',
        'ardabil',
        'yazd',
        'zanjan',
        'isfahan',
        'tehran',
        'shiraz',
        'mashhad',
        'ahvaz',
        'hamadan',
        'kurdistan',
        'karaj',
        'bandarabbas',
        'bushehr',
        'semnan',
        'golestan',
        'gilan',
        'mazandaran',
        'orumiyeh',
    ];

    register_rest_field($post_types, 'meta', [
        'get_callback' => function ($post) {
            return get_post_meta($post['id']);
        },
        'schema' => null,
    ]);
});
/////////////////////////////////
add_action('rest_api_init', function () {
    $post_types = [
        'post',
        'zahedan',
        'shahrekord',
        'arak',
        'qazvin',
        'ardabil',
        'yazd',
        'zanjan',
        'isfahan',
        'tehran',
        'shiraz',
        'mashhad',
        'ahvaz',
        'hamadan',
        'kurdistan',
        'karaj',
        'bandarabbas',
        'bushehr',
        'semnan',
        'golestan',
        'gilan',
        'mazandaran',
        'orumiyeh',
    ];

    register_rest_field($post_types, 'featured_image_url', [
        'get_callback' => function ($post_arr) {
            $thumb_id = get_post_thumbnail_id($post_arr['id']);
            $thumb_url = wp_get_attachment_image_src($thumb_id, 'full');
            return $thumb_url ? $thumb_url[0] : null;
        },
        'schema' => null,
    ]);
});
////////////////////////////

// افزودن فیلدهای Rank Math SEO به REST API
add_action('rest_api_init', function () {
    $post_types = [
        'post',
        'zahedan',
        'shahrekord',
        'arak',
        'qazvin',
        'ardabil',
        'yazd',
        'zanjan',
        'isfahan',
        'tehran',
        'shiraz',
        'mashhad',
        'ahvaz',
        'hamadan',
        'kurdistan',
        'karaj',
        'bandarabbas',
        'bushehr',
        'semnan',
        'golestan',
        'gilan',
        'mazandaran',
        'orumiyeh',
    ];

    foreach ($post_types as $type) {
        // عنوان سئو
        register_rest_field($type, 'rank_math_title', [
            'get_callback' => function ($post) {
                return get_post_meta($post['id'], 'rank_math_title', true);
            },
            'schema' => null,
        ]);

        // توضیحات متا
        register_rest_field($type, 'rank_math_description', [
            'get_callback' => function ($post) {
                return get_post_meta($post['id'], 'rank_math_description', true);
            },
            'schema' => null,
        ]);

        // کلمه کلیدی فوکوس
        register_rest_field($type, 'rank_math_focus_keyword', [
            'get_callback' => function ($post) {
                return get_post_meta($post['id'], 'rank_math_focus_keyword', true);
            },
            'schema' => null,
        ]);
    }
});
///////////////////////////////////

add_action('rest_api_init', function () {
    // List of post types to apply the meta fields to
    $post_types = [
        'post',
        'zahedan',
        'shahrekord',
        'arak',
        'qazvin',
        'ardabil',
        'yazd',
        'zanjan',
        'isfahan',
        'tehran',
        'shiraz',
        'mashhad',
        'ahvaz',
        'hamadan',
        'kurdistan',
        'karaj',
        'bandarabbas',
        'bushehr',
        'semnan',
        'golestan',
        'gilan',
        'mazandaran',
        'orumiyeh',
    ];

    // Rank Math SEO fields to expose in REST API
    $rank_math_fields = [
        'rank_math_focus_keyword' => 'string',
        'rank_math_description' => 'string',
        'rank_math_title' => 'string',
    ];

    foreach ($post_types as $post_type) {
        foreach ($rank_math_fields as $field => $type) {
            register_post_meta($post_type, $field, [
                'type' => $type,
                'single' => true,
                'show_in_rest' => true,
                'auth_callback' => function () {
                    // Allow editing for users with 'edit_posts' or via application passwords
                    return current_user_can('edit_posts') || wp_is_application_passwords_available();
                },
            ]);
        }
    }
});

/////////////////////////////////////
function auto_generate_faq_schema_from_details($content) {
    if (is_singular() && strpos($content, '<details>') !== false) {

        // استخراج سوال و جواب از HTML
        preg_match_all('/<details>\s*<summary>(.*?)<\/summary>\s*(.*?)<\/details>/is', $content, $matches, PREG_SET_ORDER);

        if (!empty($matches)) {
            $faq_data = [];

            foreach ($matches as $match) {
                $question = wp_strip_all_tags($match[1]);
                $answer = wp_strip_all_tags($match[2]);

                $faq_data[] = [
                    "@type" => "Question",
                    "name" => $question,
                    "acceptedAnswer" => [
                        "@type" => "Answer",
                        "text" => $answer
                    ]
                ];
            }

            // ساخت JSON-LD
            $faq_schema = [
                "@context" => "https://schema.org",
                "@type" => "FAQPage",
                "mainEntity" => $faq_data
            ];

            // اضافه‌کردن اسکیما به محتوای پست
            $content .= '<script type="application/ld+json">' . json_encode($faq_schema, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT) . '</script>';
        }
    }

    return $content;
}
add_filter('the_content', 'auto_generate_faq_schema_from_details');


//////////////////////////
/**
 * افزودن هدرهای امنیتی به وردپرس
 */
function add_custom_security_headers() {
    // جلوگیری از ارسال هدرها در محیط توسعه محلی
    if ( defined( 'WP_ENVIRONMENT_TYPE' ) && WP_ENVIRONMENT_TYPE === 'local' ) {
        return;
    }

    // 1. هدر HSTS (فقط در صورت اتصال HTTPS ارسال می‌شود)
    // max-age بر حسب ثانیه است. 31536000 معادل یک سال می‌باشد.
    header( 'Strict-Transport-Security: max-age=31536000; includeSubDomains' );

    // 2. هدر X-Frame-Options (برای جلوگیری از Clickjacking)
    header( 'X-Frame-Options: SAMEORIGIN' );

    // 3. هدر Cross-Origin-Opener-Policy (COOP)
    header( 'Cross-Origin-Opener-Policy: same-origin' );

    // 4. هدر Content-Security-Policy (CSP)
    // این یک نمونه ابتدایی است. برای تنظیم دقیق، نیاز به بررسی منابع سایت خود دارید.
    $csp = "default-src 'self'; ";
    $csp .= "script-src 'self' 'unsafe-inline' https://trusted.cdn.com; ";
    $csp .= "style-src 'self' 'unsafe-inline'; ";
    $csp .= "img-src 'self' data: https:; ";
    $csp .= "font-src 'self' https:; ";
    $csp .= "frame-ancestors 'self';"; // جایگزین X-Frame-Options در CSP
    
    header( 'Content-Security-Policy: ' . $csp );
}
add_action( 'send_headers', 'add_custom_security_headers' );
///////////////////////////////////////////////////

/**
 * Navaraby language context fix.
 * Add at the end of the active child-theme functions.php.
 * Detects the language from translated page/product/post metadata first,
 * then from language slugs/query values, so menus do not fall back to Persian.
 */
if (!defined('ABSPATH')) { exit; }

function navaraby_ctx_lang() {
    $id = get_queried_object_id();
    if ($id) {
        $meta = get_post_meta($id, '_navar_translation_language', true);
        if ($meta === 'ar-IQ') return 'ar-IQ';
        if ($meta === 'tg-TJ') return 'tg-TJ';
    }

    $q = '';
    if (isset($_GET['navar_lang'])) $q = strtolower(sanitize_key(wp_unslash($_GET['navar_lang'])));
    elseif (isset($_GET['lang'])) $q = strtolower(sanitize_key(wp_unslash($_GET['lang'])));
    if (in_array($q, array('iraq','ar','ar-iq'), true)) return 'ar-IQ';
    if (in_array($q, array('tj','tajik','tg','tg-tj'), true)) return 'tg-TJ';

    $path = strtolower(trim((string) parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH), '/'));
    if (strpos($path, 'ar-iq-') === 0 || strpos($path, 'maqalat-al-ray') !== false) return 'ar-IQ';
    if (strpos($path, 'tg-tj-') === 0 || strpos($path, 'maqolahoi-obyor') !== false) return 'tg-TJ';

    $obj = get_queried_object();
    if ($obj && !empty($obj->slug)) {
        if (in_array($obj->slug, array('iraq','maqalat-al-ray'), true)) return 'ar-IQ';
        if (in_array($obj->slug, array('tj','tajik','tajikistan','maqolahoi-obyor'), true)) return 'tg-TJ';
    }
    return 'fa-IR';
}

function navaraby_ctx_short_lang() {
    $lang = navaraby_ctx_lang();
    return $lang === 'ar-IQ' ? 'iraq' : ($lang === 'tg-TJ' ? 'tj' : 'fa');
}

// Make the document language and direction authoritative.
add_filter('language_attributes', function ($output, $doctype) {
    $lang = navaraby_ctx_lang();
    if ($lang === 'tg-TJ') {
        $output = preg_replace('/\blang=("|\')[^"\']*\1/i', 'lang="tg-TJ"', $output);
        $output = preg_replace('/\bdir=("|\')[^"\']*\1/i', 'dir="ltr"', $output);
        if (strpos($output, 'lang="tg-TJ"') === false) $output .= ' lang="tg-TJ"';
        if (strpos($output, 'dir="ltr"') === false) $output .= ' dir="ltr"';
    } elseif ($lang === 'ar-IQ') {
        $output = preg_replace('/\blang=("|\')[^"\']*\1/i', 'lang="ar-IQ"', $output);
        $output = preg_replace('/\bdir=("|\')[^"\']*\1/i', 'dir="rtl"', $output);
        if (strpos($output, 'lang="ar-IQ"') === false) $output .= ' lang="ar-IQ"';
        if (strpos($output, 'dir="rtl"') === false) $output .= ' dir="rtl"';
    }
    return $output;
}, 99, 2);

add_filter('body_class', function ($classes) {
    $lang = navaraby_ctx_lang();
    $classes[] = $lang === 'tg-TJ' ? 'navar-lang-tj navar-dir-ltr' : ($lang === 'ar-IQ' ? 'navar-lang-iraq navar-dir-rtl' : 'navar-lang-fa');
    return $classes;
}, 99);

// Force Tajik LTR after the existing navar-v2 stylesheet has loaded.
add_action('wp_enqueue_scripts', function () {
    if (navaraby_ctx_lang() !== 'tg-TJ') return;
    $css = 'html[lang^="tg"], html[lang^="tg"] body, body.navar-lang-tj { direction:ltr !important; }'
        . 'html[lang^="tg"] body, body.navar-lang-tj { text-align:left; }'
        . 'html[lang^="tg"] .site-header, html[lang^="tg"] .site-content, html[lang^="tg"] .site-footer, body.navar-lang-tj .site-header, body.navar-lang-tj .site-content, body.navar-lang-tj .site-footer { direction:ltr !important; }'
        . 'html[lang^="tg"] .main-navigation ul, body.navar-lang-tj .main-navigation ul { direction:ltr !important; }';
    if (wp_style_is('navar-v2', 'enqueued')) wp_add_inline_style('navar-v2', $css);
}, 99);

// Translate every menu item from the custom metadata already used by the SQL patch.
add_filter('wp_nav_menu_objects', function ($items, $args) {
    $lang = navaraby_ctx_lang();
    $title_key = $lang === 'ar-IQ' ? '_navar_menu_title_iraq' : ($lang === 'tg-TJ' ? '_navar_menu_title_tj' : '');
    $url_key = $lang === 'ar-IQ' ? '_navar_menu_url_iraq' : ($lang === 'tg-TJ' ? '_navar_menu_url_tj' : '');
    if (!$title_key) return $items;

    foreach ($items as $item) {
        $title = trim((string) get_post_meta($item->ID, $title_key, true));
        $url = trim((string) get_post_meta($item->ID, $url_key, true));
        if ($title !== '') {
            $item->title = $title;
            $item->post_title = $title;
        }
        if ($url !== '') $item->url = $url;
    }
    return $items;
}, 100, 2);
