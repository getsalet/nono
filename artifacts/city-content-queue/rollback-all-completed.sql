-- Marker-protected rollback.
SET NAMES utf8mb4;
USE `navaraby_wp569`;
SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10000010001108-layflat' WHERE p.post_name='زاویه-مرکزی-looleh-nakhi-tashoo' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10000010001108-tape20' WHERE p.post_name='زاویه-مرکزی-navar-tip-20cm' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10000010001109-layflat' WHERE p.post_name='مامونیه-مرکزی-looleh-nakhi-tashoo' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10000010001109-tape20' WHERE p.post_name='مامونیه-مرکزی-navar-tip-20cm' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10000010002017-layflat' WHERE p.post_name='خشکرود-مرکزی-looleh-nakhi-tashoo' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10000010002017-tape20' WHERE p.post_name='خشکرود-مرکزی-navar-tip-20cm' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10000010002228-layflat' WHERE p.post_name='پرندک-مرکزی-looleh-nakhi-tashoo' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10000010002228-tape20' WHERE p.post_name='پرندک-مرکزی-navar-tip-20cm' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10000010002378-layflat' WHERE p.post_name='رازقان-مرکزی-looleh-nakhi-tashoo' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10000010002378-tape20' WHERE p.post_name='رازقان-مرکزی-navar-tip-20cm' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1000001001600-layflat' WHERE p.post_name='کارچان-مرکزی-looleh-nakhi-tashoo' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1000001001600-tape20' WHERE p.post_name='کارچان-مرکزی-navar-tip-20cm' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1000001002074-layflat' WHERE p.post_name='ساروق-مرکزی-looleh-nakhi-tashoo' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1000001002074-tape20' WHERE p.post_name='ساروق-مرکزی-navar-tip-20cm' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1000001002536-layflat' WHERE p.post_name='داودآباد-مرکزی-looleh-nakhi-tashoo' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1000001002536-tape20' WHERE p.post_name='داودآباد-مرکزی-navar-tip-20cm' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10000011002379-layflat' WHERE p.post_name='میلاجرد-مرکزی-looleh-nakhi-tashoo' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10000011002379-tape20' WHERE p.post_name='میلاجرد-مرکزی-navar-tip-20cm' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10000012002073-layflat' WHERE p.post_name='جاورسیان-مرکزی-looleh-nakhi-tashoo' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10000012002073-tape20' WHERE p.post_name='جاورسیان-مرکزی-navar-tip-20cm' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10000013002136-layflat' WHERE p.post_name='فرمهین-مرکزی-looleh-nakhi-tashoo' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10000013002136-tape20' WHERE p.post_name='فرمهین-مرکزی-navar-tip-20cm' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10000013002773-layflat' WHERE p.post_name='خنجین-مرکزی-looleh-nakhi-tashoo' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10000013002773-tape20' WHERE p.post_name='خنجین-مرکزی-navar-tip-20cm' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10000013002941-layflat' WHERE p.post_name='تلخاب-مرکزی-looleh-nakhi-tashoo' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10000013002941-tape20' WHERE p.post_name='تلخاب-مرکزی-navar-tip-20cm' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1000005001107-layflat' WHERE p.post_name='نراق-مرکزی-looleh-nakhi-tashoo' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1000005001107-tape20' WHERE p.post_name='نراق-مرکزی-navar-tip-20cm' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1000006002137-layflat' WHERE p.post_name='نوبران-مرکزی-looleh-nakhi-tashoo' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1000006002137-tape20' WHERE p.post_name='نوبران-مرکزی-navar-tip-20cm' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1000006002827-layflat' WHERE p.post_name='آوه-مرکزی-looleh-nakhi-tashoo' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1000006002827-tape20' WHERE p.post_name='آوه-مرکزی-navar-tip-20cm' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1000007001112-layflat' WHERE p.post_name='آستانه-مرکزی-looleh-nakhi-tashoo' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1000007001112-tape20' WHERE p.post_name='آستانه-مرکزی-navar-tip-20cm' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1000007002032-layflat' WHERE p.post_name='مهاجران-مرکزی-looleh-nakhi-tashoo' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1000007002032-tape20' WHERE p.post_name='مهاجران-مرکزی-navar-tip-20cm' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1000007002380-layflat' WHERE p.post_name='هندودر-مرکزی-looleh-nakhi-tashoo' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1000007002380-tape20' WHERE p.post_name='هندودر-مرکزی-navar-tip-20cm' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1000007002582-layflat' WHERE p.post_name='توره-مرکزی-looleh-nakhi-tashoo' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1000007002582-tape20' WHERE p.post_name='توره-مرکزی-navar-tip-20cm' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1000007002774-layflat' WHERE p.post_name='شهباز-مرکزی-looleh-nakhi-tashoo' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1000007002774-tape20' WHERE p.post_name='شهباز-مرکزی-navar-tip-20cm' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1000009001116-layflat' WHERE p.post_name='نیمور-مرکزی-looleh-nakhi-tashoo' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1000009001116-tape20' WHERE p.post_name='نیمور-مرکزی-navar-tip-20cm' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10100010001144-layflat' WHERE p.post_name='کومله-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10100010001144-tape20' WHERE p.post_name='کومله-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10100010001145-layflat' WHERE p.post_name='لنگرود-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10100010001145-tape20' WHERE p.post_name='لنگرود-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10100010002141-layflat' WHERE p.post_name='شلمان-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10100010002141-tape20' WHERE p.post_name='شلمان-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10100010002385-layflat' WHERE p.post_name='اطاقور-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10100010002385-tape20' WHERE p.post_name='اطاقور-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010001001117-layflat' WHERE p.post_name='آستارا-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010001001117-tape20' WHERE p.post_name='آستارا-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010001002583-layflat' WHERE p.post_name='لوندویل-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010001002583-tape20' WHERE p.post_name='لوندویل-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10100011001147-layflat' WHERE p.post_name='لاهیجان-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10100011001147-tape20' WHERE p.post_name='لاهیجان-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10100011002386-layflat' WHERE p.post_name='رودبنه-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10100011002386-tape20' WHERE p.post_name='رودبنه-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10100012001141-layflat' WHERE p.post_name='شفت-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10100012001141-tape20' WHERE p.post_name='شفت-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10100013001134-layflat' WHERE p.post_name='املش-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10100013001134-tape20' WHERE p.post_name='املش-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10100013002519-layflat' WHERE p.post_name='رانکوه-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10100013002519-tape20' WHERE p.post_name='رانکوه-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10100014001122-layflat' WHERE p.post_name='رضوانشهر-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10100014001122-tape20' WHERE p.post_name='رضوانشهر-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10100015001146-layflat' WHERE p.post_name='سیاهکل-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10100015001146-tape20' WHERE p.post_name='سیاهکل-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10100015002329-layflat' WHERE p.post_name='دیلمان-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10100015002329-tape20' WHERE p.post_name='دیلمان-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10100016001123-layflat' WHERE p.post_name='ماسال-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10100016001123-tape20' WHERE p.post_name='ماسال-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10100017001060-layflat' WHERE p.post_name='چوکام-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10100017001060-tape20' WHERE p.post_name='چوکام-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10100017001126-layflat' WHERE p.post_name='خمام-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10100017001126-tape20' WHERE p.post_name='خمام-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010002001118-layflat' WHERE p.post_name='کیاشهر-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010002001118-tape20' WHERE p.post_name='کیاشهر-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010003001120-layflat' WHERE p.post_name='بندرانزلی-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010003001120-tape20' WHERE p.post_name='بندرانزلی-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010004002381-layflat' WHERE p.post_name='لیسار-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010004002381-tape20' WHERE p.post_name='لیسار-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010004002382-layflat' WHERE p.post_name='اسالم-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010004002382-tape20' WHERE p.post_name='اسالم-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010004002584-layflat' WHERE p.post_name='حویق-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010004002584-tape20' WHERE p.post_name='حویق-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010004002585-layflat' WHERE p.post_name='چوبر-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010004002585-tape20' WHERE p.post_name='چوبر-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010005001007-layflat' WHERE p.post_name='پیربازار-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010005001007-tape20' WHERE p.post_name='پیربازار-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010005001125-layflat' WHERE p.post_name='خشکبیجار-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010005001125-tape20' WHERE p.post_name='خشکبیجار-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010005001127-layflat' WHERE p.post_name='کوچصفهان-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010005001127-tape20' WHERE p.post_name='کوچصفهان-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010005001129-layflat' WHERE p.post_name='رشت-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010005001129-tape20' WHERE p.post_name='رشت-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010005001130-layflat' WHERE p.post_name='سنگر-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010005001130-tape20' WHERE p.post_name='سنگر-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010005002075-layflat' WHERE p.post_name='لولمان-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010005002075-tape20' WHERE p.post_name='لولمان-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010006001131-layflat' WHERE p.post_name='لوشان-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010006001131-tape20' WHERE p.post_name='لوشان-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010006001132-layflat' WHERE p.post_name='رودبار-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010006001132-tape20' WHERE p.post_name='رودبار-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010006001133-layflat' WHERE p.post_name='منجیل-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010006001133-tape20' WHERE p.post_name='منجیل-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010006002138-layflat' WHERE p.post_name='جیرنده-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010006002138-tape20' WHERE p.post_name='جیرنده-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010006002229-layflat' WHERE p.post_name='توتکابن-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010006002229-tape20' WHERE p.post_name='توتکابن-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010007001135-layflat' WHERE p.post_name='چابکسر-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010007001135-tape20' WHERE p.post_name='چابکسر-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010007001137-layflat' WHERE p.post_name='رودسر-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010007001137-tape20' WHERE p.post_name='رودسر-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010007001138-layflat' WHERE p.post_name='کلاچای-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010007001138-tape20' WHERE p.post_name='کلاچای-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010007001139-layflat' WHERE p.post_name='واجارگاه-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010007001139-tape20' WHERE p.post_name='واجارگاه-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010008001059-layflat' WHERE p.post_name='ضیابر-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010008001059-tape20' WHERE p.post_name='ضیابر-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010008002140-layflat' WHERE p.post_name='مرجقل-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010008002140-tape20' WHERE p.post_name='مرجقل-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010009001142-layflat' WHERE p.post_name='فومن-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010009001142-tape20' WHERE p.post_name='فومن-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010009001143-layflat' WHERE p.post_name='ماسوله-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010009001143-tape20' WHERE p.post_name='ماسوله-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010009002804-layflat' WHERE p.post_name='ماکلوان-گیلان-looleh-nakhi-tashoo' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1010009002804-tape20' WHERE p.post_name='ماکلوان-گیلان-navar-tip-20cm' AND p.post_type='gilan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200010002747-layflat' WHERE p.post_name='ارطه-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200010002747-tape20' WHERE p.post_name='ارطه-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020001001148-layflat' WHERE p.post_name='رینه-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020001001148-tape20' WHERE p.post_name='رینه-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020001001149-layflat' WHERE p.post_name='آمل-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020001001149-tape20' WHERE p.post_name='آمل-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020001002388-layflat' WHERE p.post_name='گزنک-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020001002388-tape20' WHERE p.post_name='گزنک-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020001002586-layflat' WHERE p.post_name='دابودشت-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020001002586-tape20' WHERE p.post_name='دابودشت-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020001002875-layflat' WHERE p.post_name='بابکان-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020001002875-tape20' WHERE p.post_name='بابکان-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200014001189-layflat' WHERE p.post_name='نور-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200014001189-tape20' WHERE p.post_name='نور-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200014001193-layflat' WHERE p.post_name='رویان-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200014001193-tape20' WHERE p.post_name='رویان-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200014002119-layflat' WHERE p.post_name='چمستان-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200014002119-tape20' WHERE p.post_name='چمستان-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200014002396-layflat' WHERE p.post_name='بلده-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200014002396-tape20' WHERE p.post_name='بلده-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200014002648-layflat' WHERE p.post_name='ایزدشهر-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200014002648-tape20' WHERE p.post_name='ایزدشهر-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200015001194-layflat' WHERE p.post_name='نوشهر-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200015001194-tape20' WHERE p.post_name='نوشهر-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200015002779-layflat' WHERE p.post_name='کجور-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200015002779-tape20' WHERE p.post_name='کجور-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200016001151-layflat' WHERE p.post_name='بابلسر-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200016001151-tape20' WHERE p.post_name='بابلسر-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200016002393-layflat' WHERE p.post_name='بهنمیر-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200016002393-tape20' WHERE p.post_name='بهنمیر-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200018002395-layflat' WHERE p.post_name='سرخرود-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200018002395-tape20' WHERE p.post_name='سرخرود-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200020001190-layflat' WHERE p.post_name='چالوس-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200020001190-tape20' WHERE p.post_name='چالوس-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200020002748-layflat' WHERE p.post_name='هچیرود-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200020002748-tape20' WHERE p.post_name='هچیرود-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020002001153-layflat' WHERE p.post_name='امیرکلا-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020002001153-tape20' WHERE p.post_name='امیرکلا-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020002001154-layflat' WHERE p.post_name='بابل-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020002001154-tape20' WHERE p.post_name='بابل-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020002002390-layflat' WHERE p.post_name='گلوگاه-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020002002390-tape20' WHERE p.post_name='گلوگاه-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020002002391-layflat' WHERE p.post_name='مرزیکلا-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020002002391-tape20' WHERE p.post_name='مرزیکلا-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020002002392-layflat' WHERE p.post_name='زرگر-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020002002392-tape20' WHERE p.post_name='زرگر-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020002002587-layflat' WHERE p.post_name='گتاب-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020002002587-tape20' WHERE p.post_name='گتاب-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200021001175-layflat' WHERE p.post_name='جویبار-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200021001175-tape20' WHERE p.post_name='جویبار-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200023001152-layflat' WHERE p.post_name='فریدونکنار-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200023001152-tape20' WHERE p.post_name='فریدونکنار-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200024001165-layflat' WHERE p.post_name='کلارآباد-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200024001165-tape20' WHERE p.post_name='کلارآباد-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200025002305-layflat' WHERE p.post_name='سورک-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200025002305-tape20' WHERE p.post_name='سورک-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200025002931-layflat' WHERE p.post_name='طبقده-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200025002931-tape20' WHERE p.post_name='طبقده-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200026001177-layflat' WHERE p.post_name='کیاکلا-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200026001177-tape20' WHERE p.post_name='کیاکلا-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200027001173-layflat' WHERE p.post_name='شیرگاه-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200027001173-tape20' WHERE p.post_name='شیرگاه-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200028001191-layflat' WHERE p.post_name='کلاردشت-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10200028001191-tape20' WHERE p.post_name='کلاردشت-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020004001158-layflat' WHERE p.post_name='بهشهر-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020004001158-tape20' WHERE p.post_name='بهشهر-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020004001159-layflat' WHERE p.post_name='رستمکلا-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020004001159-tape20' WHERE p.post_name='رستمکلا-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020005001100-layflat' WHERE p.post_name='شیرود-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020005001100-tape20' WHERE p.post_name='شیرود-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020005001161-layflat' WHERE p.post_name='تنکابن-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020005001161-tape20' WHERE p.post_name='تنکابن-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020005001166-layflat' WHERE p.post_name='نشتارود-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020005001166-tape20' WHERE p.post_name='نشتارود-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020006001069-layflat' WHERE p.post_name='دالخانی-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020006001069-tape20' WHERE p.post_name='دالخانی-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020006001167-layflat' WHERE p.post_name='رامسر-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020006001167-tape20' WHERE p.post_name='رامسر-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020007001006-layflat' WHERE p.post_name='اکند-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020007001006-tape20' WHERE p.post_name='اکند-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020007002170-layflat' WHERE p.post_name='کیاسر-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020007002170-tape20' WHERE p.post_name='کیاسر-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020008001170-layflat' WHERE p.post_name='آلاشت-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020008001170-tape20' WHERE p.post_name='آلاشت-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020008001172-layflat' WHERE p.post_name='زیرآب-مازندران-looleh-nakhi-tashoo' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1020008001172-tape20' WHERE p.post_name='زیرآب-مازندران-navar-tip-20cm' AND p.post_type='mazandaran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300010001233-layflat' WHERE p.post_name='میانه-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300010001233-tape20' WHERE p.post_name='میانه-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300010002144-layflat' WHERE p.post_name='ترکمانچای-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300010002144-tape20' WHERE p.post_name='ترکمانچای-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300010002401-layflat' WHERE p.post_name='آقکند-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300010002401-tape20' WHERE p.post_name='آقکند-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300010002842-layflat' WHERE p.post_name='اچاچی-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300010002842-tape20' WHERE p.post_name='اچاچی-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300011001234-layflat' WHERE p.post_name='هشترود-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300011001234-tape20' WHERE p.post_name='هشترود-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300011002590-layflat' WHERE p.post_name='نظرکهریزی-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300011002590-tape20' WHERE p.post_name='نظرکهریزی-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300012001221-layflat' WHERE p.post_name='بناب-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300012001221-tape20' WHERE p.post_name='بناب-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300013001025-layflat' WHERE p.post_name='کردکندی-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300013001025-tape20' WHERE p.post_name='کردکندی-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300014001208-layflat' WHERE p.post_name='تسوج-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300014001208-tape20' WHERE p.post_name='تسوج-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300014001209-layflat' WHERE p.post_name='خامنه-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300014001209-tape20' WHERE p.post_name='خامنه-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300014001210-layflat' WHERE p.post_name='شبستر-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300014001210-tape20' WHERE p.post_name='شبستر-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300014001211-layflat' WHERE p.post_name='شرفخانه-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300014001211-tape20' WHERE p.post_name='شرفخانه-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300014001212-layflat' WHERE p.post_name='صوفیان-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300014001212-tape20' WHERE p.post_name='صوفیان-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300014002101-layflat' WHERE p.post_name='شندآباد-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300014002101-tape20' WHERE p.post_name='شندآباد-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300014002149-layflat' WHERE p.post_name='وایقان-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300014002149-tape20' WHERE p.post_name='وایقان-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300014002946-layflat' WHERE p.post_name='داریان-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300014002946-tape20' WHERE p.post_name='داریان-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300014002947-layflat' WHERE p.post_name='علیشاه-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300014002947-tape20' WHERE p.post_name='علیشاه-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300015001199-layflat' WHERE p.post_name='کلیبر-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300015001199-tape20' WHERE p.post_name='کلیبر-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300016001217-layflat' WHERE p.post_name='هریس-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300016001217-tape20' WHERE p.post_name='هریس-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300016002146-layflat' WHERE p.post_name='خواجه-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300016002146-tape20' WHERE p.post_name='خواجه-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300016002147-layflat' WHERE p.post_name='زرنق-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300016002147-tape20' WHERE p.post_name='زرنق-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300016002230-layflat' WHERE p.post_name='بخشایش-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300016002230-tape20' WHERE p.post_name='بخشایش-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300016002333-layflat' WHERE p.post_name='کلوانق-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300016002333-tape20' WHERE p.post_name='کلوانق-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300016002935-layflat' WHERE p.post_name='اربطان-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300016002935-tape20' WHERE p.post_name='اربطان-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300019001225-layflat' WHERE p.post_name='جلفا-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300019001225-tape20' WHERE p.post_name='جلفا-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300019001226-layflat' WHERE p.post_name='هادیشهر-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300019001226-tape20' WHERE p.post_name='هادیشهر-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300020001224-layflat' WHERE p.post_name='ملکان-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300020001224-tape20' WHERE p.post_name='ملکان-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1030002001200-layflat' WHERE p.post_name='اهر-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1030002001200-tape20' WHERE p.post_name='اهر-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300021001201-layflat' WHERE p.post_name='آذرشهر-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300021001201-tape20' WHERE p.post_name='آذرشهر-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300021001202-layflat' WHERE p.post_name='گوگان-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300021001202-tape20' WHERE p.post_name='گوگان-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300021001203-layflat' WHERE p.post_name='ممقان-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300021001203-tape20' WHERE p.post_name='ممقان-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300021002763-layflat' WHERE p.post_name='تیمورلو-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300021002763-tape20' WHERE p.post_name='تیمورلو-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300022001204-layflat' WHERE p.post_name='اسکو-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300022001204-tape20' WHERE p.post_name='اسکو-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300022001205-layflat' WHERE p.post_name='ایلخچی-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300022001205-tape20' WHERE p.post_name='ایلخچی-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300022002033-layflat' WHERE p.post_name='سهند-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300022002033-tape20' WHERE p.post_name='سهند-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300024002142-layflat' WHERE p.post_name='ورزقان-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300024002142-tape20' WHERE p.post_name='ورزقان-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300024002398-layflat' WHERE p.post_name='خاروانا-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300024002398-tape20' WHERE p.post_name='خاروانا-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300026002332-layflat' WHERE p.post_name='خمارلو-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300026002332-tape20' WHERE p.post_name='خمارلو-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300026002944-layflat' WHERE p.post_name='عاشقلو-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300026002944-tape20' WHERE p.post_name='عاشقلو-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300026002945-layflat' WHERE p.post_name='لاریجان-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300026002945-tape20' WHERE p.post_name='لاریجان-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300027002294-layflat' WHERE p.post_name='هوراند-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300027002294-tape20' WHERE p.post_name='هوراند-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300028002296-layflat' WHERE p.post_name='لیلان-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10300028002296-tape20' WHERE p.post_name='لیلان-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1030003001067-layflat' WHERE p.post_name='اسفهلان-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1030003001067-tape20' WHERE p.post_name='اسفهلان-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1030003001068-layflat' WHERE p.post_name='لاهیجان-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1030003001068-tape20' WHERE p.post_name='لاهیجان-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1030003001206-layflat' WHERE p.post_name='خسروشاه-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1030003001206-tape20' WHERE p.post_name='خسروشاه-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1030003001213-layflat' WHERE p.post_name='باسمنج-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1030003001213-tape20' WHERE p.post_name='باسمنج-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1030003001214-layflat' WHERE p.post_name='تبریز-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1030003001214-tape20' WHERE p.post_name='تبریز-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1030003001215-layflat' WHERE p.post_name='سردرود-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1030003001215-tape20' WHERE p.post_name='سردرود-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1030005001216-layflat' WHERE p.post_name='مهربان-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1030005001216-tape20' WHERE p.post_name='مهربان-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1030005001220-layflat' WHERE p.post_name='سراب-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1030005001220-tape20' WHERE p.post_name='سراب-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1030005002330-layflat' WHERE p.post_name='شربیان-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1030005002330-tape20' WHERE p.post_name='شربیان-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1030005002399-layflat' WHERE p.post_name='دوزدوزان-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1030005002399-tape20' WHERE p.post_name='دوزدوزان-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1030006001223-layflat' WHERE p.post_name='مراغه-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1030006001223-tape20' WHERE p.post_name='مراغه-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1030006002331-layflat' WHERE p.post_name='خداجوخراجو-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1030006002331-tape20' WHERE p.post_name='خداجوخراجو-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1030007001227-layflat' WHERE p.post_name='زنوز-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1030007001227-tape20' WHERE p.post_name='زنوز-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1030007001228-layflat' WHERE p.post_name='مرند-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1030007001228-tape20' WHERE p.post_name='مرند-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1030007002143-layflat' WHERE p.post_name='کشکسرای-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1030007002143-tape20' WHERE p.post_name='کشکسرای-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1030007002400-layflat' WHERE p.post_name='یامچی-آذربایجان-شرقی-looleh-nakhi-tashoo' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1030007002400-tape20' WHERE p.post_name='یامچی-آذربایجان-شرقی-navar-tip-20cm' AND p.post_type='east_azarbaijan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10400010001247-layflat' WHERE p.post_name='بوکان-آذربایجان-غربی-looleh-nakhi-tashoo' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10400010001247-tape20' WHERE p.post_name='بوکان-آذربایجان-غربی-navar-tip-20cm' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10400010002548-layflat' WHERE p.post_name='سیمینه-آذربایجان-غربی-looleh-nakhi-tashoo' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10400010002548-tape20' WHERE p.post_name='سیمینه-آذربایجان-غربی-navar-tip-20cm' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1040001002150-layflat' WHERE p.post_name='قوشچی-آذربایجان-غربی-looleh-nakhi-tashoo' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1040001002150-tape20' WHERE p.post_name='قوشچی-آذربایجان-غربی-navar-tip-20cm' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1040001002151-layflat' WHERE p.post_name='نوشین-آذربایجان-غربی-looleh-nakhi-tashoo' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1040001002151-tape20' WHERE p.post_name='نوشین-آذربایجان-غربی-navar-tip-20cm' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1040001002403-layflat' WHERE p.post_name='سیلوانه-آذربایجان-غربی-looleh-nakhi-tashoo' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1040001002403-tape20' WHERE p.post_name='سیلوانه-آذربایجان-غربی-navar-tip-20cm' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1040001002404-layflat' WHERE p.post_name='سرو-آذربایجان-غربی-looleh-nakhi-tashoo' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1040001002404-tape20' WHERE p.post_name='سرو-آذربایجان-غربی-navar-tip-20cm' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10400012001249-layflat' WHERE p.post_name='تکاب-آذربایجان-غربی-looleh-nakhi-tashoo' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10400012001249-tape20' WHERE p.post_name='تکاب-آذربایجان-غربی-navar-tip-20cm' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10400013001252-layflat' WHERE p.post_name='اشنویه-آذربایجان-غربی-looleh-nakhi-tashoo' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10400013001252-tape20' WHERE p.post_name='اشنویه-آذربایجان-غربی-navar-tip-20cm' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10400013002408-layflat' WHERE p.post_name='نالوس-آذربایجان-غربی-looleh-nakhi-tashoo' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10400013002408-tape20' WHERE p.post_name='نالوس-آذربایجان-غربی-navar-tip-20cm' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10400017001244-layflat' WHERE p.post_name='شوط-آذربایجان-غربی-looleh-nakhi-tashoo' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10400017001244-tape20' WHERE p.post_name='شوط-آذربایجان-غربی-navar-tip-20cm' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10400017002736-layflat' WHERE p.post_name='مرگنلر-آذربایجان-غربی-looleh-nakhi-tashoo' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10400017002736-tape20' WHERE p.post_name='مرگنلر-آذربایجان-غربی-navar-tip-20cm' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10400017002899-layflat' WHERE p.post_name='یولاگلدی-آذربایجان-غربی-looleh-nakhi-tashoo' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10400017002899-tape20' WHERE p.post_name='یولاگلدی-آذربایجان-غربی-navar-tip-20cm' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10400019002592-layflat' WHERE p.post_name='باروق-آذربایجان-غربی-looleh-nakhi-tashoo' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10400019002592-tape20' WHERE p.post_name='باروق-آذربایجان-غربی-navar-tip-20cm' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10400020002406-layflat' WHERE p.post_name='میرآباد-آذربایجان-غربی-looleh-nakhi-tashoo' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10400020002406-tape20' WHERE p.post_name='میرآباد-آذربایجان-غربی-navar-tip-20cm' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1040002001236-layflat' WHERE p.post_name='پیرانشهر-آذربایجان-غربی-looleh-nakhi-tashoo' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1040003001238-layflat' WHERE p.post_name='خوی-آذربایجان-غربی-looleh-nakhi-tashoo' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1040003001238-tape20' WHERE p.post_name='خوی-آذربایجان-غربی-navar-tip-20cm' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1040003001239-layflat' WHERE p.post_name='فیرورق-آذربایجان-غربی-looleh-nakhi-tashoo' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1040003001239-tape20' WHERE p.post_name='فیرورق-آذربایجان-غربی-navar-tip-20cm' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1040003002044-layflat' WHERE p.post_name='قطور-آذربایجان-غربی-looleh-nakhi-tashoo' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1040003002044-tape20' WHERE p.post_name='قطور-آذربایجان-غربی-navar-tip-20cm' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1040003002405-layflat' WHERE p.post_name='ایواوغلی-آذربایجان-غربی-looleh-nakhi-tashoo' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1040003002405-tape20' WHERE p.post_name='ایواوغلی-آذربایجان-غربی-navar-tip-20cm' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1040004001240-layflat' WHERE p.post_name='سردشت-آذربایجان-غربی-looleh-nakhi-tashoo' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1040004001240-tape20' WHERE p.post_name='سردشت-آذربایجان-غربی-navar-tip-20cm' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1040004002922-layflat' WHERE p.post_name='نلاس-آذربایجان-غربی-looleh-nakhi-tashoo' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1040004002922-tape20' WHERE p.post_name='نلاس-آذربایجان-غربی-navar-tip-20cm' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1040005001242-layflat' WHERE p.post_name='سلماس-آذربایجان-غربی-looleh-nakhi-tashoo' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1040005001242-tape20' WHERE p.post_name='سلماس-آذربایجان-غربی-navar-tip-20cm' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1040006001246-layflat' WHERE p.post_name='ماکو-آذربایجان-غربی-looleh-nakhi-tashoo' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1040006001246-tape20' WHERE p.post_name='ماکو-آذربایجان-غربی-navar-tip-20cm' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1040006002231-layflat' WHERE p.post_name='بازرگان-آذربایجان-غربی-looleh-nakhi-tashoo' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1040006002231-tape20' WHERE p.post_name='بازرگان-آذربایجان-غربی-navar-tip-20cm' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1040007001248-layflat' WHERE p.post_name='مهاباد-آذربایجان-غربی-looleh-nakhi-tashoo' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1040007001248-tape20' WHERE p.post_name='مهاباد-آذربایجان-غربی-navar-tip-20cm' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1040007002734-layflat' WHERE p.post_name='خلیفان-آذربایجان-غربی-looleh-nakhi-tashoo' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1040007002734-tape20' WHERE p.post_name='خلیفان-آذربایجان-غربی-navar-tip-20cm' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1040008001005-layflat' WHERE p.post_name='بکتاش-آذربایجان-غربی-looleh-nakhi-tashoo' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1040008001005-tape20' WHERE p.post_name='بکتاش-آذربایجان-غربی-navar-tip-20cm' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1040008001251-layflat' WHERE p.post_name='میاندوآب-آذربایجان-غربی-looleh-nakhi-tashoo' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1040008001251-tape20' WHERE p.post_name='میاندوآب-آذربایجان-غربی-navar-tip-20cm' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1040009001253-layflat' WHERE p.post_name='محمدیار-آذربایجان-غربی-looleh-nakhi-tashoo' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1040009001253-tape20' WHERE p.post_name='محمدیار-آذربایجان-غربی-navar-tip-20cm' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1040009001254-tape20' WHERE p.post_name='نقده-آذربایجان-غربی-navar-tip-20cm' AND p.post_type='orumiyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10500010001257-tape20' WHERE p.post_name='صحنه-کرمانشاه-navar-tip-20cm' AND p.post_type='kermanshah' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10500010002414-layflat' WHERE p.post_name='دینور-کرمانشاه-looleh-nakhi-tashoo' AND p.post_type='kermanshah' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10500011002233-tape20' WHERE p.post_name='بیستون-کرمانشاه-navar-tip-20cm' AND p.post_type='kermanshah' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10500012002593-tape20' WHERE p.post_name='ازگله-کرمانشاه-navar-tip-20cm' AND p.post_type='kermanshah' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10500012002977-tape20' WHERE p.post_name='میرآباد-کرمانشاه-navar-tip-20cm' AND p.post_type='kermanshah' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10500013001255-tape20' WHERE p.post_name='کرند-کرمانشاه-navar-tip-20cm' AND p.post_type='kermanshah' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10500013002409-tape20' WHERE p.post_name='گهواره-کرمانشاه-navar-tip-20cm' AND p.post_type='kermanshah' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10500014002034-layflat' WHERE p.post_name='شاهو-کرمانشاه-looleh-nakhi-tashoo' AND p.post_type='kermanshah' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10500014002034-tape20' WHERE p.post_name='شاهو-کرمانشاه-navar-tip-20cm' AND p.post_type='kermanshah' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10500014002102-layflat' WHERE p.post_name='روانسر-کرمانشاه-looleh-nakhi-tashoo' AND p.post_type='kermanshah' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10500014002102-tape20' WHERE p.post_name='روانسر-کرمانشاه-navar-tip-20cm' AND p.post_type='kermanshah' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1050002002410-layflat' WHERE p.post_name='هلشی-کرمانشاه-looleh-nakhi-tashoo' AND p.post_type='kermanshah' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1050002002412-tape20' WHERE p.post_name='کوزران-کرمانشاه-navar-tip-20cm' AND p.post_type='kermanshah' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1050002002896-tape20' WHERE p.post_name='قلعه-کرمانشاه-navar-tip-20cm' AND p.post_type='kermanshah' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1050003001261-layflat' WHERE p.post_name='پاوه-کرمانشاه-looleh-nakhi-tashoo' AND p.post_type='kermanshah' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1050003001263-layflat' WHERE p.post_name='نوسود-کرمانشاه-looleh-nakhi-tashoo' AND p.post_type='kermanshah' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1050003001263-tape20' WHERE p.post_name='نوسود-کرمانشاه-navar-tip-20cm' AND p.post_type='kermanshah' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1050003002761-layflat' WHERE p.post_name='بانوره-کرمانشاه-looleh-nakhi-tashoo' AND p.post_type='kermanshah' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1050005001265-layflat' WHERE p.post_name='سنقر-کرمانشاه-looleh-nakhi-tashoo' AND p.post_type='kermanshah' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1050005001265-tape20' WHERE p.post_name='سنقر-کرمانشاه-navar-tip-20cm' AND p.post_type='kermanshah' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1050006001266-tape20' WHERE p.post_name='قصرشیرین-کرمانشاه-navar-tip-20cm' AND p.post_type='kermanshah' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1050006002197-layflat' WHERE p.post_name='سومار-کرمانشاه-looleh-nakhi-tashoo' AND p.post_type='kermanshah' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1050006002197-tape20' WHERE p.post_name='سومار-کرمانشاه-navar-tip-20cm' AND p.post_type='kermanshah' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1050007001267-tape20' WHERE p.post_name='کنگاور-کرمانشاه-navar-tip-20cm' AND p.post_type='kermanshah' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1050007002834-tape20' WHERE p.post_name='گودین-کرمانشاه-navar-tip-20cm' AND p.post_type='kermanshah' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1050008001268-layflat' WHERE p.post_name='گیلانغرب-کرمانشاه-looleh-nakhi-tashoo' AND p.post_type='kermanshah' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1050008002413-tape20' WHERE p.post_name='سرمست-کرمانشاه-navar-tip-20cm' AND p.post_type='kermanshah' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10600010001004-layflat' WHERE p.post_name='باوج-خوزستان-looleh-nakhi-tashoo' AND p.post_type='ahvaz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1060001001269-tape20' WHERE p.post_name='اروندکنار-خوزستان-navar-tip-20cm' AND p.post_type='ahvaz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1060001001270-tape20' WHERE p.post_name='آبادان-خوزستان-navar-tip-20cm' AND p.post_type='ahvaz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1060001002010-tape20' WHERE p.post_name='چویبده-خوزستان-navar-tip-20cm' AND p.post_type='ahvaz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10600011002008-tape20' WHERE p.post_name='دارخوین-خوزستان-navar-tip-20cm' AND p.post_type='ahvaz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10600011002794-tape20' WHERE p.post_name='خنافره-خوزستان-navar-tip-20cm' AND p.post_type='ahvaz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10600012002036-tape20' WHERE p.post_name='شرافت-خوزستان-navar-tip-20cm' AND p.post_type='ahvaz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10600012002792-tape20' WHERE p.post_name='سرداران-خوزستان-navar-tip-20cm' AND p.post_type='ahvaz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10600017001061-tape20' WHERE p.post_name='تراز-خوزستان-navar-tip-20cm' AND p.post_type='ahvaz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10600018002650-tape20' WHERE p.post_name='زهره-خوزستان-navar-tip-20cm' AND p.post_type='ahvaz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1060002002595-tape20' WHERE p.post_name='حسینیه-خوزستان-navar-tip-20cm' AND p.post_type='ahvaz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1060002002803-tape20' WHERE p.post_name='بیدروبه-خوزستان-navar-tip-20cm' AND p.post_type='ahvaz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10600021002799-layflat' WHERE p.post_name='آبژدان-خوزستان-looleh-nakhi-tashoo' AND p.post_type='ahvaz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10600021002928-tape20' WHERE p.post_name='زاووت-خوزستان-navar-tip-20cm' AND p.post_type='ahvaz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10600022001292-tape20' WHERE p.post_name='هفتگل-خوزستان-navar-tip-20cm' AND p.post_type='ahvaz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10600023002313-layflat' WHERE p.post_name='رفیع-خوزستان-looleh-nakhi-tashoo' AND p.post_type='ahvaz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10600023002313-tape20' WHERE p.post_name='رفیع-خوزستان-navar-tip-20cm' AND p.post_type='ahvaz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10600024002310-tape20' WHERE p.post_name='شیبان-خوزستان-navar-tip-20cm' AND p.post_type='ahvaz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10600026001278-tape20' WHERE p.post_name='آغاجاری-خوزستان-navar-tip-20cm' AND p.post_type='ahvaz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10600026002920-layflat' WHERE p.post_name='جولکی-خوزستان-looleh-nakhi-tashoo' AND p.post_type='ahvaz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10600026002920-tape20' WHERE p.post_name='جولکی-خوزستان-navar-tip-20cm' AND p.post_type='ahvaz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10600028002037-layflat' WHERE p.post_name='شاوور-خوزستان-looleh-nakhi-tashoo' AND p.post_type='ahvaz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10600028002037-tape20' WHERE p.post_name='شاوور-خوزستان-navar-tip-20cm' AND p.post_type='ahvaz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10600028002314-layflat' WHERE p.post_name='الوان-خوزستان-looleh-nakhi-tashoo' AND p.post_type='ahvaz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10600028002314-tape20' WHERE p.post_name='الوان-خوزستان-navar-tip-20cm' AND p.post_type='ahvaz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1060005001276-layflat' WHERE p.post_name='بندرماهشهر-خوزستان-looleh-nakhi-tashoo' AND p.post_type='ahvaz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1060005001276-tape20' WHERE p.post_name='بندرماهشهر-خوزستان-navar-tip-20cm' AND p.post_type='ahvaz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1060006002500-tape20' WHERE p.post_name='سردشت-خوزستان-navar-tip-20cm' AND p.post_type='ahvaz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1060006002797-tape20' WHERE p.post_name='منصوریه-خوزستان-navar-tip-20cm' AND p.post_type='ahvaz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1060006002798-tape20' WHERE p.post_name='تشان-خوزستان-navar-tip-20cm' AND p.post_type='ahvaz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1060007002312-tape20' WHERE p.post_name='مینوشهر-خوزستان-navar-tip-20cm' AND p.post_type='ahvaz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1060007002334-tape20' WHERE p.post_name='مقاومت-خوزستان-navar-tip-20cm' AND p.post_type='ahvaz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1060008002416-tape20' WHERE p.post_name='سالند-خوزستان-navar-tip-20cm' AND p.post_type='ahvaz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1060008002419-tape20' WHERE p.post_name='میانرود-خوزستان-navar-tip-20cm' AND p.post_type='ahvaz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1060008002927-tape20' WHERE p.post_name='شهیون-خوزستان-navar-tip-20cm' AND p.post_type='ahvaz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1060008002967-tape20' WHERE p.post_name='منتظران-خوزستان-navar-tip-20cm' AND p.post_type='ahvaz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10700010002109-tape20' WHERE p.post_name='خشت-فارس-navar-tip-20cm' AND p.post_type='shiraz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10700010002423-tape20' WHERE p.post_name='بالاده-فارس-navar-tip-20cm' AND p.post_type='shiraz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1070001002597-tape20' WHERE p.post_name='سورمق-فارس-navar-tip-20cm' AND p.post_type='shiraz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10700011002013-tape20' WHERE p.post_name='لطیفی-فارس-navar-tip-20cm' AND p.post_type='shiraz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10700012002555-layflat' WHERE p.post_name='کامفیروز-فارس-looleh-nakhi-tashoo' AND p.post_type='shiraz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10700012002951-layflat' WHERE p.post_name='فاروق-فارس-looleh-nakhi-tashoo' AND p.post_type='shiraz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10700014002058-tape20' WHERE p.post_name='قطرویه-فارس-navar-tip-20cm' AND p.post_type='shiraz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10700015002212-tape20' WHERE p.post_name='اشکنان-فارس-navar-tip-20cm' AND p.post_type='shiraz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1070002002177-tape20' WHERE p.post_name='رونیز-فارس-navar-tip-20cm' AND p.post_type='shiraz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10700021002708-tape20' WHERE p.post_name='اسیر-فارس-navar-tip-20cm' AND p.post_type='shiraz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10700021002820-layflat' WHERE p.post_name='خوزی-فارس-looleh-nakhi-tashoo' AND p.post_type='shiraz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10700027001319-tape20' WHERE p.post_name='گراش-فارس-navar-tip-20cm' AND p.post_type='shiraz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10700028001042-layflat' WHERE p.post_name='اکبرآباد-فارس-looleh-nakhi-tashoo' AND p.post_type='shiraz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10700028001307-tape20' WHERE p.post_name='کوار-فارس-navar-tip-20cm' AND p.post_type='shiraz' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10800010002824-tape20' WHERE p.post_name='دشتکار-کرمان-navar-tip-20cm' AND p.post_type='kerman' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10800011001340-tape20' WHERE p.post_name='راور-کرمان-navar-tip-20cm' AND p.post_type='kerman' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10800013002240-tape20' WHERE p.post_name='منوجان-کرمان-navar-tip-20cm' AND p.post_type='kerman' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10800014001336-tape20' WHERE p.post_name='کوهبنان-کرمان-navar-tip-20cm' AND p.post_type='kerman' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10800014002110-layflat' WHERE p.post_name='کیانشهر-کرمان-looleh-nakhi-tashoo' AND p.post_type='kerman' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10800014002110-tape20' WHERE p.post_name='کیانشهر-کرمان-navar-tip-20cm' AND p.post_type='kerman' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10800018002771-tape20' WHERE p.post_name='هنزا-کرمان-navar-tip-20cm' AND p.post_type='kerman' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1080002001079-tape20' WHERE p.post_name='دهبکری-کرمان-navar-tip-20cm' AND p.post_type='kerman' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10800022002429-tape20' WHERE p.post_name='فاریاب-کرمان-navar-tip-20cm' AND p.post_type='kerman' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1080003002237-tape20' WHERE p.post_name='جبالبارز-کرمان-navar-tip-20cm' AND p.post_type='kerman' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1080005002201-layflat' WHERE p.post_name='خانوک-کرمان-looleh-nakhi-tashoo' AND p.post_type='kerman' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1080006002825-layflat' WHERE p.post_name='بلورد-کرمان-looleh-nakhi-tashoo' AND p.post_type='kerman' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1080007002031-tape20' WHERE p.post_name='جوزم-کرمان-navar-tip-20cm' AND p.post_type='kerman' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1080008001341-layflat' WHERE p.post_name='شهداد-کرمان-looleh-nakhi-tashoo' AND p.post_type='kerman' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10900013001041-tape20' WHERE p.post_name='مزرج-خراسان-رضوی-navar-tip-20cm' AND p.post_type='mashhad' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10900013001376-layflat' WHERE p.post_name='باجگیران-خراسان-رضوی-looleh-nakhi-tashoo' AND p.post_type='mashhad' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10900015001383-layflat' WHERE p.post_name='بیدخت-خراسان-رضوی-looleh-nakhi-tashoo' AND p.post_type='mashhad' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10900018002999-layflat' WHERE p.post_name='سیدآباد-خراسان-رضوی-looleh-nakhi-tashoo' AND p.post_type='mashhad' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10900018002999-tape20' WHERE p.post_name='سیدآباد-خراسان-رضوی-navar-tip-20cm' AND p.post_type='mashhad' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10900019002605-tape20' WHERE p.post_name='سلامی-خراسان-رضوی-navar-tip-20cm' AND p.post_type='mashhad' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10900029002656-tape20' WHERE p.post_name='کندر-خراسان-رضوی-navar-tip-20cm' AND p.post_type='mashhad' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10900031002610-tape20' WHERE p.post_name='یونسی-خراسان-رضوی-navar-tip-20cm' AND p.post_type='mashhad' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='10900037002134-layflat' WHERE p.post_name='باخرز-خراسان-رضوی-looleh-nakhi-tashoo' AND p.post_type='mashhad' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1090006002342-tape20' WHERE p.post_name='نصرآباد-خراسان-رضوی-navar-tip-20cm' AND p.post_type='mashhad' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='11000012002112-tape20' WHERE p.post_name='ورنامخواست-اصفهان-navar-tip-20cm' AND p.post_type='isfahan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='11000013002078-tape20' WHERE p.post_name='بافران-اصفهان-navar-tip-20cm' AND p.post_type='isfahan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='11000014002570-tape20' WHERE p.post_name='کهریزسنگ-اصفهان-navar-tip-20cm' AND p.post_type='isfahan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='11000017001599-tape20' WHERE p.post_name='مجلسی-اصفهان-navar-tip-20cm' AND p.post_type='isfahan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='11000018002279-layflat' WHERE p.post_name='ابوزیدآباد-اصفهان-looleh-nakhi-tashoo' AND p.post_type='isfahan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='11000018002279-tape20' WHERE p.post_name='ابوزیدآباد-اصفهان-navar-tip-20cm' AND p.post_type='isfahan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='11000020002352-layflat' WHERE p.post_name='رزوه-اصفهان-looleh-nakhi-tashoo' AND p.post_type='isfahan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1100002002611-tape20' WHERE p.post_name='بهارستان-اصفهان-navar-tip-20cm' AND p.post_type='isfahan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='11000021002093-layflat' WHERE p.post_name='گلشن-اصفهان-looleh-nakhi-tashoo' AND p.post_type='isfahan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='11000022002756-layflat' WHERE p.post_name='سین-اصفهان-looleh-nakhi-tashoo' AND p.post_type='isfahan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='11000022002756-tape20' WHERE p.post_name='سین-اصفهان-navar-tip-20cm' AND p.post_type='isfahan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='11000025002513-layflat' WHERE p.post_name='تودشک-اصفهان-looleh-nakhi-tashoo' AND p.post_type='isfahan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='11000028002248-tape20' WHERE p.post_name='اژیه-اصفهان-navar-tip-20cm' AND p.post_type='isfahan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1100003002755-layflat' WHERE p.post_name='اصغرآباد-اصفهان-looleh-nakhi-tashoo' AND p.post_type='isfahan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1100005002249-tape20' WHERE p.post_name='حنا-اصفهان-navar-tip-20cm' AND p.post_type='isfahan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1100005002923-tape20' WHERE p.post_name='بیده-اصفهان-navar-tip-20cm' AND p.post_type='isfahan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1100008002789-tape20' WHERE p.post_name='زازران-اصفهان-navar-tip-20cm' AND p.post_type='isfahan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1100009002446-tape20' WHERE p.post_name='منظریه-اصفهان-navar-tip-20cm' AND p.post_type='isfahan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='11100010002978-tape20' WHERE p.post_name='جزینک-سیستان-و-بلوچستان-navar-tip-20cm' AND p.post_type='zahedan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='11100011002916-tape20' WHERE p.post_name='قرقری-سیستان-و-بلوچستان-navar-tip-20cm' AND p.post_type='zahedan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='11100012002451-tape20' WHERE p.post_name='گلمورتی-سیستان-و-بلوچستان-navar-tip-20cm' AND p.post_type='zahedan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='11100014002174-layflat' WHERE p.post_name='سوران-سیستان-و-بلوچستان-looleh-nakhi-tashoo' AND p.post_type='zahedan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='11100017001078-tape20' WHERE p.post_name='لادیز-سیستان-و-بلوچستان-navar-tip-20cm' AND p.post_type='zahedan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='11100019002913-layflat' WHERE p.post_name='گتیج-سیستان-و-بلوچستان-looleh-nakhi-tashoo' AND p.post_type='zahedan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='11100019002913-tape20' WHERE p.post_name='گتیج-سیستان-و-بلوچستان-navar-tip-20cm' AND p.post_type='zahedan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='11100020002049-layflat' WHERE p.post_name='محمدان-سیستان-و-بلوچستان-looleh-nakhi-tashoo' AND p.post_type='zahedan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='11100020002049-tape20' WHERE p.post_name='محمدان-سیستان-و-بلوچستان-navar-tip-20cm' AND p.post_type='zahedan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='11100024002191-layflat' WHERE p.post_name='جالق-سیستان-و-بلوچستان-looleh-nakhi-tashoo' AND p.post_type='zahedan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='11100024002191-tape20' WHERE p.post_name='جالق-سیستان-و-بلوچستان-navar-tip-20cm' AND p.post_type='zahedan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1110005002891-layflat' WHERE p.post_name='سرجنگل-سیستان-و-بلوچستان-looleh-nakhi-tashoo' AND p.post_type='zahedan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1110006001047-layflat' WHERE p.post_name='اسفندک-سیستان-و-بلوچستان-looleh-nakhi-tashoo' AND p.post_type='zahedan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1110006002455-tape20' WHERE p.post_name='سیرکان-سیستان-و-بلوچستان-navar-tip-20cm' AND p.post_type='zahedan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1110007001001-tape20' WHERE p.post_name='چانف-سیستان-و-بلوچستان-navar-tip-20cm' AND p.post_type='zahedan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1110008002890-layflat' WHERE p.post_name='پارود-سیستان-و-بلوچستان-looleh-nakhi-tashoo' AND p.post_type='zahedan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1120003001456-tape20' WHERE p.post_name='سقز-کردستان-navar-tip-20cm' AND p.post_type='kurdistan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1120003002502-layflat' WHERE p.post_name='صاحب-کردستان-looleh-nakhi-tashoo' AND p.post_type='kurdistan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1120003002924-tape20' WHERE p.post_name='سنته-کردستان-navar-tip-20cm' AND p.post_type='kurdistan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1120005002463-tape20' WHERE p.post_name='دزج-کردستان-navar-tip-20cm' AND p.post_type='kurdistan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1120006001463-layflat' WHERE p.post_name='مریوان-کردستان-looleh-nakhi-tashoo' AND p.post_type='kurdistan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1120007001459-layflat' WHERE p.post_name='دیواندره-کردستان-looleh-nakhi-tashoo' AND p.post_type='kurdistan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1120007001459-tape20' WHERE p.post_name='دیواندره-کردستان-navar-tip-20cm' AND p.post_type='kurdistan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1120007002925-tape20' WHERE p.post_name='هزارکانیان-کردستان-navar-tip-20cm' AND p.post_type='kurdistan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1120008001457-tape20' WHERE p.post_name='کامیاران-کردستان-navar-tip-20cm' AND p.post_type='kurdistan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1120009002205-layflat' WHERE p.post_name='سروآباد-کردستان-looleh-nakhi-tashoo' AND p.post_type='kurdistan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1130006002994-tape20' WHERE p.post_name='پالیز-همدان-navar-tip-20cm' AND p.post_type='hamadan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1130008002357-layflat' WHERE p.post_name='دمق-همدان-looleh-nakhi-tashoo' AND p.post_type='hamadan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1130008002357-tape20' WHERE p.post_name='دمق-همدان-navar-tip-20cm' AND p.post_type='hamadan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1140001002152-tape20' WHERE p.post_name='گندمان-چهارمحال-و-بختیاری-navar-tip-20cm' AND p.post_type='shahrekord' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1140002002471-tape20' WHERE p.post_name='نافچ-چهارمحال-و-بختیاری-navar-tip-20cm' AND p.post_type='shahrekord' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1140002002614-layflat' WHERE p.post_name='سودجان-چهارمحال-و-بختیاری-looleh-nakhi-tashoo' AND p.post_type='shahrekord' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1140002002838-tape20' WHERE p.post_name='هارونی-چهارمحال-و-بختیاری-navar-tip-20cm' AND p.post_type='shahrekord' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1140004002840-layflat' WHERE p.post_name='سردشت-چهارمحال-و-بختیاری-looleh-nakhi-tashoo' AND p.post_type='shahrekord' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1140005002807-tape20' WHERE p.post_name='کاج-چهارمحال-و-بختیاری-navar-tip-20cm' AND p.post_type='shahrekord' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1140006002839-tape20' WHERE p.post_name='صمصامی-چهارمحال-و-بختیاری-navar-tip-20cm' AND p.post_type='shahrekord' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1140006002841-layflat' WHERE p.post_name='بازفت-چهارمحال-و-بختیاری-looleh-nakhi-tashoo' AND p.post_type='shahrekord' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1140007002358-tape20' WHERE p.post_name='گهرو-چهارمحال-و-بختیاری-navar-tip-20cm' AND p.post_type='shahrekord' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1150001002877-tape20' WHERE p.post_name='شاهپوراباد-لرستان-navar-tip-20cm' AND p.post_type='lorestan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1150003002474-tape20' WHERE p.post_name='سپیددشت-لرستان-navar-tip-20cm' AND p.post_type='lorestan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1150006002257-layflat' WHERE p.post_name='گراب-لرستان-looleh-nakhi-tashoo' AND p.post_type='lorestan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1150007001488-tape20' WHERE p.post_name='ازنا-لرستان-navar-tip-20cm' AND p.post_type='lorestan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1150008001497-layflat' WHERE p.post_name='پلدختر-لرستان-looleh-nakhi-tashoo' AND p.post_type='lorestan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='11600012001499-tape20' WHERE p.post_name='چوار-ایلام-navar-tip-20cm' AND p.post_type='ilam' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1160003001506-layflat' WHERE p.post_name='موسیان-ایلام-looleh-nakhi-tashoo' AND p.post_type='ilam' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1160004001507-layflat' WHERE p.post_name='سرابله-ایلام-looleh-nakhi-tashoo' AND p.post_type='ilam' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1160004002850-layflat' WHERE p.post_name='شباب-ایلام-looleh-nakhi-tashoo' AND p.post_type='ilam' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1160004002851-tape20' WHERE p.post_name='بلاوه-ایلام-navar-tip-20cm' AND p.post_type='ilam' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1160007001498-tape20' WHERE p.post_name='ایوان-ایلام-navar-tip-20cm' AND p.post_type='ilam' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1160007002476-layflat' WHERE p.post_name='زرنه-ایلام-looleh-nakhi-tashoo' AND p.post_type='ilam' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1160007002476-tape20' WHERE p.post_name='زرنه-ایلام-navar-tip-20cm' AND p.post_type='ilam' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1160008002028-tape20' WHERE p.post_name='دلگشا-ایلام-navar-tip-20cm' AND p.post_type='ilam' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1160009002155-tape20' WHERE p.post_name='لومار-ایلام-navar-tip-20cm' AND p.post_type='ilam' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1170002001514-tape20' WHERE p.post_name='دهدشت-کهگیلویه-و-بویراحمد-navar-tip-20cm' AND p.post_type='kohgiluyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1170002002480-tape20' WHERE p.post_name='دیشموک-کهگیلویه-و-بویراحمد-navar-tip-20cm' AND p.post_type='kohgiluyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1170003001515-tape20' WHERE p.post_name='دوگنبدان-کهگیلویه-و-بویراحمد-navar-tip-20cm' AND p.post_type='kohgiluyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1170005002368-tape20' WHERE p.post_name='لیکک-کهگیلویه-و-بویراحمد-navar-tip-20cm' AND p.post_type='kohgiluyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1170006002828-tape20' WHERE p.post_name='سرفاریاب-کهگیلویه-و-بویراحمد-navar-tip-20cm' AND p.post_type='kohgiluyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1170008002129-tape20' WHERE p.post_name='لنده-کهگیلویه-و-بویراحمد-navar-tip-20cm' AND p.post_type='kohgiluyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1170009002477-tape20' WHERE p.post_name='مارگون-کهگیلویه-و-بویراحمد-navar-tip-20cm' AND p.post_type='kohgiluyeh' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1180001002481-layflat' WHERE p.post_name='چغادک-بوشهر-looleh-nakhi-tashoo' AND p.post_type='bushehr' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1180001002481-tape20' WHERE p.post_name='چغادک-بوشهر-navar-tip-20cm' AND p.post_type='bushehr' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1180003002369-layflat' WHERE p.post_name='دالکی-بوشهر-looleh-nakhi-tashoo' AND p.post_type='bushehr' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1180003002369-tape20' WHERE p.post_name='دالکی-بوشهر-navar-tip-20cm' AND p.post_type='bushehr' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1180003002482-tape20' WHERE p.post_name='وحدتیه-بوشهر-navar-tip-20cm' AND p.post_type='bushehr' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1180004001521-tape20' WHERE p.post_name='خورموج-بوشهر-navar-tip-20cm' AND p.post_type='bushehr' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1180004002818-layflat' WHERE p.post_name='بادوله-بوشهر-looleh-nakhi-tashoo' AND p.post_type='bushehr' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1180005002483-layflat' WHERE p.post_name='بردخون-بوشهر-looleh-nakhi-tashoo' AND p.post_type='bushehr' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1180006002661-tape20' WHERE p.post_name='سیراف-بوشهر-navar-tip-20cm' AND p.post_type='bushehr' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1180009002087-tape20' WHERE p.post_name='انارستان-بوشهر-navar-tip-20cm' AND p.post_type='bushehr' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1190001001531-tape20' WHERE p.post_name='هیدج-زنجان-navar-tip-20cm' AND p.post_type='zanjan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1190003002260-tape20' WHERE p.post_name='گرماب-زنجان-navar-tip-20cm' AND p.post_type='zanjan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1190003002833-tape20' WHERE p.post_name='نوربهار-زنجان-navar-tip-20cm' AND p.post_type='zanjan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1200001001540-tape20' WHERE p.post_name='دامغان-سمنان-navar-tip-20cm' AND p.post_type='semnan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1200003001546-layflat' WHERE p.post_name='مجن-سمنان-looleh-nakhi-tashoo' AND p.post_type='semnan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1200003002775-layflat' WHERE p.post_name='رودیان-سمنان-looleh-nakhi-tashoo' AND p.post_type='semnan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1200003002775-tape20' WHERE p.post_name='رودیان-سمنان-navar-tip-20cm' AND p.post_type='semnan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1200007002162-layflat' WHERE p.post_name='میامی-سمنان-looleh-nakhi-tashoo' AND p.post_type='semnan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1200007002162-tape20' WHERE p.post_name='میامی-سمنان-navar-tip-20cm' AND p.post_type='semnan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1200008001541-layflat' WHERE p.post_name='سرخه-سمنان-looleh-nakhi-tashoo' AND p.post_type='semnan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='12100013001561-tape20' WHERE p.post_name='زارچ-یزد-navar-tip-20cm' AND p.post_type='yazd' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1210006002024-layflat' WHERE p.post_name='بفروییه-یزد-looleh-nakhi-tashoo' AND p.post_type='yazd' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1210006002024-tape20' WHERE p.post_name='بفروییه-یزد-navar-tip-20cm' AND p.post_type='yazd' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1210008002377-layflat' WHERE p.post_name='خضرآباد-یزد-looleh-nakhi-tashoo' AND p.post_type='yazd' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='12200010001564-tape20' WHERE p.post_name='خمیر-هرمزگان-navar-tip-20cm' AND p.post_type='bandarabbas' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='12200010002005-layflat' WHERE p.post_name='رویدر-هرمزگان-looleh-nakhi-tashoo' AND p.post_type='bandarabbas' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1220001001563-layflat' WHERE p.post_name='ابوموسی-هرمزگان-looleh-nakhi-tashoo' AND p.post_type='bandarabbas' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='12200012002724-tape20' WHERE p.post_name='گروک-هرمزگان-navar-tip-20cm' AND p.post_type='bandarabbas' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='12200012002815-layflat' WHERE p.post_name='کوهستک-هرمزگان-looleh-nakhi-tashoo' AND p.post_type='bandarabbas' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1220003001570-layflat' WHERE p.post_name='کنگ-هرمزگان-looleh-nakhi-tashoo' AND p.post_type='bandarabbas' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1220003002813-layflat' WHERE p.post_name='لمزان-هرمزگان-looleh-nakhi-tashoo' AND p.post_type='bandarabbas' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1220005001575-layflat' WHERE p.post_name='میناب-هرمزگان-looleh-nakhi-tashoo' AND p.post_type='bandarabbas' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1220007002663-layflat' WHERE p.post_name='زیارتعلی-هرمزگان-looleh-nakhi-tashoo' AND p.post_type='bandarabbas' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='12300012002666-layflat' WHERE p.post_name='نصیرشهر-تهران-looleh-nakhi-tashoo' AND p.post_type='tehran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='12300014001577-tape20' WHERE p.post_name='فیروزکوه-تهران-navar-tip-20cm' AND p.post_type='tehran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='12300014002634-layflat' WHERE p.post_name='ارجمند-تهران-looleh-nakhi-tashoo' AND p.post_type='tehran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='12300014002634-tape20' WHERE p.post_name='ارجمند-تهران-navar-tip-20cm' AND p.post_type='tehran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='12300016002116-layflat' WHERE p.post_name='قدس-تهران-looleh-nakhi-tashoo' AND p.post_type='tehran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='12300016002116-tape20' WHERE p.post_name='قدس-تهران-navar-tip-20cm' AND p.post_type='tehran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='12300019002278-tape20' WHERE p.post_name='گلستان-تهران-navar-tip-20cm' AND p.post_type='tehran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1230003002270-tape20' WHERE p.post_name='باقرشهر-تهران-navar-tip-20cm' AND p.post_type='tehran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1230006002168-layflat' WHERE p.post_name='جوادآباد-تهران-looleh-nakhi-tashoo' AND p.post_type='tehran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1230009002632-tape20' WHERE p.post_name='باغستان-تهران-navar-tip-20cm' AND p.post_type='tehran' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='12400010002881-layflat' WHERE p.post_name='اردیموسی-اردبیل-looleh-nakhi-tashoo' AND p.post_type='ardabil' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1240001002882-layflat' WHERE p.post_name='ثمرین-اردبیل-looleh-nakhi-tashoo' AND p.post_type='ardabil' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='12400012001065-layflat' WHERE p.post_name='زیوه-اردبیل-looleh-nakhi-tashoo' AND p.post_type='ardabil' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='12400012001065-tape20' WHERE p.post_name='زیوه-اردبیل-navar-tip-20cm' AND p.post_type='ardabil' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1240003002164-tape20' WHERE p.post_name='هشتجین-اردبیل-navar-tip-20cm' AND p.post_type='ardabil' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1240004002704-layflat' WHERE p.post_name='فخراباد-اردبیل-looleh-nakhi-tashoo' AND p.post_type='ardabil' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1240006001032-layflat' WHERE p.post_name='اولتان-اردبیل-looleh-nakhi-tashoo' AND p.post_type='ardabil' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1260001001538-layflat' WHERE p.post_name='شال-قزوین-looleh-nakhi-tashoo' AND p.post_type='qazvin' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1260005001539-layflat' WHERE p.post_name='الوند-قزوین-looleh-nakhi-tashoo' AND p.post_type='qazvin' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='12700010001182-tape20' WHERE p.post_name='آزادشهر-گلستان-navar-tip-20cm' AND p.post_type='golestan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1270001002194-layflat' WHERE p.post_name='نوکنده-گلستان-looleh-nakhi-tashoo' AND p.post_type='golestan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1270005001181-tape20' WHERE p.post_name='گرگان-گلستان-navar-tip-20cm' AND p.post_type='golestan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1270006001030-layflat' WHERE p.post_name='کرند-گلستان-looleh-nakhi-tashoo' AND p.post_type='golestan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1270007001188-layflat' WHERE p.post_name='مینودشت-گلستان-looleh-nakhi-tashoo' AND p.post_type='golestan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1270009002835-layflat' WHERE p.post_name='فراغی-گلستان-looleh-nakhi-tashoo' AND p.post_type='golestan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1280004001038-tape20' WHERE p.post_name='خانلق-خراسان-شمالی-navar-tip-20cm' AND p.post_type='north_khorasan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1280004001368-layflat' WHERE p.post_name='شیروان-خراسان-شمالی-looleh-nakhi-tashoo' AND p.post_type='north_khorasan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1280005002079-tape20' WHERE p.post_name='تیتکانلو-خراسان-شمالی-navar-tip-20cm' AND p.post_type='north_khorasan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1290001001355-tape20' WHERE p.post_name='بیرجند-خراسان-جنوبی-navar-tip-20cm' AND p.post_type='south_khorasan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;

SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1290007001002-tape20' WHERE p.post_name='باغستان-خراسان-جنوبی-navar-tip-20cm' AND p.post_type='south_khorasan' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;
