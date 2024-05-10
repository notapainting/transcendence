# chat/consumer/handler.py

from channels.db import database_sync_to_async

import chat.serializers as ser
import chat.models as mod
import chat.enums as enu
import chat.utils as uti

# contact
# group_create
# group_create_private

@database_sync_to_async
def contact(user, data):
    try :
        author = user
        target = mod.User.objects.get(name=data['name'])
        if author == target:
            raise DrfValidationError('forbidden self operation on contact', code=403)

        if data['operation'] == enu.Operations.REMOVE:
            author.delete_relation(target)
            target_rel = target.get_relation(author)
            if target_rel is not None and target_rel != mod.Relation.Types.BLOCK:
                target.delete_relation(author)
                # unblock p-conv

        elif data['operation'] == enu.Operations.BLOCK:
            # block p-conv
            author.update_relation(target, mod.Relation.Types.BLOCK)
            if target.get_relation(author) != mod.Relation.Types.BLOCK:
                target.delete_relation(author)

        else: # data['operation'] == enu.Operations.CONTACT or enu.Operations.INVIT
            target_rel = target.get_relation(author)
            if target_rel == mod.Relation.Types.BLOCK:
                raise DrfValidationError('your blocked, dont do this', code=403)
            elif target_rel == mod.Relation.Types.INVIT:
                author.update_relation(target, mod.Relation.Types.COMRADE)
                target.update_relation(author, mod.Relation.Types.COMRADE)
                data['operation'] = enu.Operations.CONTACT
            else:
                author.update_relation(target, mod.Relation.Types.INVIT)
                data['operation'] = enu.Operations.INVIT
        return data

    except ObjectDoesNotExist:
        raise DrfValidationError('target not found', code=404)
    except DrfValidationError:
        raise 
    except BaseException as e:
        logger.info(e.args[0])
        raise DrfValidationError('INTERNAL', code=500)

@database_sync_to_async
def group_create(user, data):
    pass

@database_sync_to_async
def group_create_private(user, data):
    logger.info(data)
    pgroup = uti.create_private_conv(user, mod.User.objects.get(name=data['target']))
    logger.info(ser.Group(pgroup).data)
    if  data.get('body', None) is not None:
        s = ser.Message(data={'author':user.name, 'group':pgroup.id, 'body':data['body']})
        s.is_valid(raise_exception=True)
        s.create(s.validated_data)
    return data['target'], ser.Group(pgroup).data
